
import React, { useState, useRef } from 'react';

const UploadArea = () => {
  const [dragOver, setDragOver] = useState(false);
  const [file, setFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleAreaClick = () => {
    fileInputRef.current.click();
  };

  const imageUrl = file ? URL.createObjectURL(file) : null;

  return (
    <div
      className={`relative h-80 w-full border-2 border-dashed rounded-lg flex items-center justify-center cursor-pointer transition-colors ${
        dragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50 hover:border-gray-400'
      }`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleAreaClick}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileInputChange}
        className="hidden"
        accept="image/*"
      />
      
      {imageUrl ? (
        <img src={imageUrl} alt="Preview" className="absolute inset-0 w-full h-full object-contain" />
      ) : (
        <p className="absolute top-1/4 left-1/4 -translate-x-1/4 -translate-y-1/4 text-gray-500 text-center">
          여기에 파일을 끌어다 놓거나 클릭하여 업로드하세요.
        </p>
      )}
    </div>
  );
};

export default UploadArea;
