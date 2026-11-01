"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { VoiceState } from "@/types/api";

interface UseVoiceRecorderOptions {
  onRecordingComplete?: (audioBlob: Blob) => void | Promise<void>;
  onError?: (errorMessage: string) => void;
}

export function useVoiceRecorder(options: UseVoiceRecorderOptions = {}) {
  const [state, setState] = useState<VoiceState>("idle");
  const [duration, setDuration] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Clean up timer and streams on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const clearTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const startRecording = useCallback(async () => {
    setErrorMessage(null);

    // Check browser support
    if (
      typeof window === "undefined" ||
      !navigator.mediaDevices ||
      !window.MediaRecorder
    ) {
      const err = "Voice recording is not supported in this browser. Please use Chrome, Edge, or Firefox.";
      setErrorMessage(err);
      setState("error");
      options.onError?.(err);
      return;
    }

    try {
      // Request permission only when user clicks record
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      streamRef.current = stream;
      setHasPermission(true);

      // Determine supported mime type
      const mimeTypes = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/ogg;codecs=opus",
        "audio/mp4",
        "audio/wav",
      ];
      const selectedMime = mimeTypes.find((type) =>
        MediaRecorder.isTypeSupported(type)
      );

      const recorder = new MediaRecorder(
        stream,
        selectedMime ? { mimeType: selectedMime } : undefined
      );
      mediaRecorderRef.current = recorder;
      audioChunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        clearTimer();
        // Stop all tracks to turn off recording indicator in browser
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((track) => track.stop());
          streamRef.current = null;
        }

        const mime = selectedMime || "audio/webm";
        const audioBlob = new Blob(audioChunksRef.current, { type: mime });

        if (audioBlob.size === 0) {
          const err = "No audio was captured. Please check your microphone.";
          setErrorMessage(err);
          setState("error");
          options.onError?.(err);
          return;
        }

        setState("processing");
        try {
          if (options.onRecordingComplete) {
            await options.onRecordingComplete(audioBlob);
          }
        } catch (err: any) {
          setErrorMessage(err.message || "Failed to process voice command");
          setState("error");
          options.onError?.(err.message || "Processing failed");
        }
      };

      recorder.start(100); // collect in 100ms chunks
      setState("recording");
      setDuration(0);

      timerRef.current = setInterval(() => {
        setDuration((prev) => prev + 1);
      }, 1000);
    } catch (err: any) {
      let friendlyError = "Could not access microphone.";
      if (
        err.name === "NotAllowedError" ||
        err.name === "PermissionDeniedError"
      ) {
        friendlyError =
          "Microphone permission was denied. Please allow microphone access in your browser settings to use voice commands.";
        setHasPermission(false);
      } else if (
        err.name === "NotFoundError" ||
        err.name === "DevicesNotFoundError"
      ) {
        friendlyError = "No microphone found. Please connect an audio input device.";
      }
      setErrorMessage(friendlyError);
      setState("error");
      options.onError?.(friendlyError);
    }
  }, [options, clearTimer]);

  const stopRecording = useCallback(() => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state === "recording"
    ) {
      mediaRecorderRef.current.stop();
    }
  }, []);

  const cancelRecording = useCallback(() => {
    clearTimer();
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      // Discard chunks before stopping
      audioChunksRef.current = [];
      mediaRecorderRef.current.stop();
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setState("idle");
    setDuration(0);
    setErrorMessage(null);
  }, [clearTimer]);

  const resetState = useCallback(() => {
    setState("idle");
    setErrorMessage(null);
    setDuration(0);
  }, []);

  return {
    state,
    setState,
    duration,
    errorMessage,
    hasPermission,
    startRecording,
    stopRecording,
    cancelRecording,
    resetState,
    isRecording: state === "recording",
    isProcessing: state === "processing" || state === "thinking",
  };
}
