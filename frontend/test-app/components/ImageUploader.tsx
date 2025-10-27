"use client";

import React, { useRef, useState, useEffect } from "react";

export default function ImageUploader() {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem("uploadedImage");
    if (saved) setPreview(saved);
  }, []);

  const openFilePicker = () => inputRef.current?.click();

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = String(reader.result);
      setPreview(dataUrl);
      localStorage.setItem("uploadedImage", dataUrl);
    };
    reader.readAsDataURL(file);
  };

  const clearImage = () => {
    setPreview(null);
    localStorage.removeItem("uploadedImage");
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <input
        type="file"
        accept="image/*"
        ref={inputRef}
        onChange={onFileChange}
        className="hidden"
      />

      <div className="flex gap-2">
        <button
          type="button"
          onClick={openFilePicker}
          className="px-4 py-2 border rounded-md shadow-sm hover:bg-gray-100"
        >
          Select Photo
        </button>
        <button
          type="button"
          onClick={clearImage}
          disabled={!preview}
          className="px-4 py-2 border rounded-md shadow-sm hover:bg-gray-100 disabled:opacity-50"
        >
          Clear
        </button>
      </div>

      {preview ? (
        <img
          src={preview}
          alt="Uploaded"
          className="w-64 h-64 object-cover rounded-md border"
        />
      ) : (
        <p className="text-gray-500">No image selected</p>
      )}
    </div>
  );
}
