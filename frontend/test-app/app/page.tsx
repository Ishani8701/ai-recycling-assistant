import Head from "next/head";
import ImageUploader from "../components/ImageUploader";

export default function Home() {
  return (
    <>
      <div className="min-h-screen flex flex-col items-center justify-center p-8">
        <h1 className="text-3xl font-bold mb-4">AI Recycling Assistant</h1>
        <p className="text mb-6 text-center max-w-md">
          This app uses computer vision to help you figure out whether a piece of trash is recyclable or not.
        </p>

        <ImageUploader />
      </div>
    </>
  );
}
