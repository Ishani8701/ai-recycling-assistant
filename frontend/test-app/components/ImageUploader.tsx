"use client";

import React, { useRef, useState, useEffect } from "react";

// ImageUploader component
// Responsibilities:
// - Provide a hidden file input to pick existing images from the device
// - Offer a "Take Photo" flow using the browser camera (getUserMedia)
// - Capture a frame from the live camera preview into a data URL and show a preview
// - Persist the preview to localStorage so it survives page reloads

export default function ImageUploader() {
  // Refs to DOM nodes
  const inputRef = useRef<HTMLInputElement | null>(null); // hidden file input
  const videoRef = useRef<HTMLVideoElement | null>(null); // <video> for live camera preview
  const canvasRef = useRef<HTMLCanvasElement | null>(null); // offscreen canvas used to capture frames

  // Component state
  const [preview, setPreview] = useState<string | null>(null); // data URL of selected/captured image
  const [cameraActive, setCameraActive] = useState(false); // whether to show camera UI
  const [stream, setStream] = useState<MediaStream | null>(null); // MediaStream from getUserMedia
  const [cameraError, setCameraError] = useState<string | null>(null); // readable camera errors
  const [cameraSupported, setCameraSupported] = useState(false); // quick feature-detect
  const [fileToUpload, setFileToUpload] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [resultText, setResultText] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // On mount: restore saved preview from localStorage and feature-detect camera support
  useEffect(() => {
    const saved = localStorage.getItem("uploadedImage");
    if (saved) setPreview(saved);

    // Feature detection: check for modern or legacy getUserMedia APIs
    try {
      const nav: any = typeof navigator !== "undefined" ? navigator : null;
      const supported = !!(
        nav &&
        ((nav.mediaDevices && typeof nav.mediaDevices.getUserMedia === "function") ||
          nav.getUserMedia ||
          nav.webkitGetUserMedia ||
          nav.mozGetUserMedia)
      );
      setCameraSupported(supported);
    } catch {
      setCameraSupported(false);
    }
  }, []);

  const openFilePicker = () => {
    console.log("File picker opened");
    inputRef.current?.click();
  };

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    // When the user selects a file, convert it to a data URL for previewing.
    // In a later change we should also keep the original `File` in state so
    // we can POST it directly to the backend without reconversion.
    reader.onload = () => {
      const dataUrl = String(reader.result);
      setPreview(dataUrl);
      localStorage.setItem("uploadedImage", dataUrl);
    };
    reader.readAsDataURL(file);
    setFileToUpload(file); // store the file for uploading
    console.log("File selected:", file);
    console.log("fileToUpload state:", fileToUpload);
  };

  const startCamera = async () => {
    setCameraError(null);

    // Try to open the camera. We only attempt this if feature-detection
    // showed some form of getUserMedia support. If it fails we'll show an
    // error to the user and leave a graceful fallback (file picker).
    if (!cameraSupported) {
      setCameraError("Camera not supported in this browser.");
      return;
    }

    try {
      const nav: any = navigator;
      const getUserMedia =
        nav.mediaDevices?.getUserMedia?.bind(nav.mediaDevices) ||
        nav.getUserMedia?.bind(nav) ||
        nav.webkitGetUserMedia?.bind(nav) ||
        nav.mozGetUserMedia?.bind(nav);

      if (!getUserMedia) {
        throw new Error("Camera API not available");
      }

      const s: MediaStream = await getUserMedia({
        video: { facingMode: "environment" },
        audio: false,
      });

      // Save stream and enable camera UI. We attach the stream to the
      // <video> element in a separate useEffect to ensure the element exists
      // before assigning srcObject (avoids visual issues in some browsers).
      setStream(s);
      setCameraActive(true);
    } catch (err: any) {
      console.error("Error accessing camera:", err);
      setCameraError(err?.message || "Could not access camera. Please allow camera permissions.");
      setCameraActive(false);
    }
  };

  // When stream becomes available and the video element is mounted, attach the stream
  // and start playback. This avoids assigning srcObject before the element exists.
  useEffect(() => {
    const video = videoRef.current;
    if (!stream || !video) return;

    video.srcObject = stream;

    const playPromise = (async () => {
      try {
        await video.play();
      } catch (e) {
        // Some browsers block autoplay until a user gesture; ignore non-fatal errors.
        console.warn('Video play() failed or was blocked:', e);
      }
    })();

    const onLoadedMetadata = () => {
      // set dimensions or perform any setup after metadata loads
      // Intentionally left blank; capture uses video.videoWidth/videoHeight when ready.
    };

    video.addEventListener('loadedmetadata', onLoadedMetadata);

    return () => {
      video.removeEventListener('loadedmetadata', onLoadedMetadata);
      try {
        // leave playing state alone; stopping handled by stopCamera
      } catch {}
    };
  }, [stream, cameraActive]);

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((t) => t.stop());
      setStream(null);
    }
    setCameraActive(false);
  };

  function dataURLtoFile(dataUrl: string, filename: string) {
    const arr = dataUrl.split(',');
    const match = arr[0].match(/:(.*?);/);
    const mime = match ? match[1] : "image/jpeg"; // fallback to jpeg if not found
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while(n--){
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, {type:mime});
  }

  const capturePhoto = () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current || document.createElement("canvas");
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL("image/jpeg");
    setPreview(dataUrl);
    localStorage.setItem("uploadedImage", dataUrl);
    stopCamera();
    const file = dataURLtoFile(dataUrl, "captured.jpg");
    setFileToUpload(file);
  };

  const clearImage = () => {
    setPreview(null);
    localStorage.removeItem("uploadedImage");
  };

  const uploadImage = async () => {
    if (!fileToUpload) {
        setUploadError("No image selected");
        return;
    }
    
    setUploading(true);
    setUploadError(null);
    setResultText(null);

    try {
        const fd = new FormData();
        fd.append("file", fileToUpload);

        const res = await fetch("http://localhost:8000/predict", {
            method: "POST",
            body: fd,
        });

        if (!res.ok) {
            const text = await res.text();
            throw new Error(`Server error: ${res.status} ${text}`);
        }
        
        const json = await res.json();
        const confidencePercent = (json.confidence * 100).toFixed(1);
        setResultText(
            `Prediction: ${json.label} (${confidencePercent}% confidence)`
        );
    } catch (err: any) {
        console.error("Upload error:", err);
        setUploadError(err?.message || "Upload failed");
    } finally {
        setUploading(false);
    }
};

  return (
    <div className="flex flex-col items-center gap-4">
      {/* Hidden File Input: used for the "Select Photo" button */}
      <input
        type="file"
        accept="image/*"
        ref={inputRef}
        onChange={onFileChange}
        className="hidden"
      />

      {/* Control Buttons: Select file, open camera, clear preview */}
      <div className="flex gap-2">
        <button
          type="button"
          onClick={openFilePicker}
          className="px-4 py-2 border rounded-md shadow-sm hover:bg-gray-100"
        >
          Select Photo
        </button>

        {/* Take Photo: opens camera preview when possible, otherwise an error is shown */}
        <button
          type="button"
          onClick={startCamera}
          title={cameraSupported ? "Open camera" : "Camera not supported"}
          className="px-4 py-2 border rounded-md shadow-sm hover:bg-gray-100"
        >
          Take Photo
        </button>

        <button
          type="button"
          onClick={clearImage}
          disabled={!preview}
          className="px-4 py-2 border rounded-md shadow-sm hover:bg-gray-100 disabled:opacity-50"
        >
          Clear
        </button>

        <button
          type="button"
          onClick={uploadImage}
          disabled={!fileToUpload || uploading}
          className="px-4 py-2 border rounded-md shadow-sm hover:bg-gray-100 disabled:opacity-50"
          >
          Upload
        </button>
      </div>

      {/* Camera Interface: shown when cameraActive is true. Live preview
          appears in the <video> element and Capture/Close buttons are shown. */}
      {cameraActive && (
        <div className="flex flex-col items-center gap-2">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className="w-64 h-64 object-cover rounded-md border bg-black"
          />
          <div className="flex gap-2">
            <button
              type="button"
              onClick={capturePhoto}
              className="px-4 py-2 border rounded-md shadow-sm hover:bg-gray-100"
            >
              Capture
            </button>
            <button
              type="button"
              onClick={stopCamera}
              className="px-4 py-2 border rounded-md shadow-sm hover:bg-gray-100"
            >
              Close Camera
            </button>
          </div>
        </div>
      )}

  {/* Camera errors are shown here to help the user troubleshoot permissions or support issues */}
  {cameraError && <p className="text-red-500">{cameraError}</p>}

      {/* Hidden Canvas */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Image Preview */}
      {preview ? (
        <img
          src={preview}
          alt="Uploaded"
          className="w-64 h-64 object-cover rounded-md border"
        />
      ) : (
        <p className="text-gray-500">No image selected</p>
      )}
      {uploadError && <p className="text-red-500">{uploadError}</p>}
      {resultText && <p className="text-blue-600 font-medium mt-2">{resultText}</p>}
    </div>
  );
}
