import { useState, useRef } from 'react';
import { Upload, X, Camera } from 'lucide-react';

interface ImageUploadProps {
  onImagesSelected: (files: File[]) => void;
  maxImages?: number;
  angle?: string;
}

const ImageUpload = ({ onImagesSelected, maxImages = 6, angle }: ImageUploadProps) => {
  const [previews, setPreviews] = useState<string[]>([]);
  const [files, setFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    
    if (files.length + selectedFiles.length > maxImages) {
      alert(`Maximum ${maxImages} images allowed`);
      return;
    }

    const newFiles = [...files, ...selectedFiles];
    setFiles(newFiles);

    // Create previews
    const newPreviews = selectedFiles.map(file => URL.createObjectURL(file));
    setPreviews([...previews, ...newPreviews]);

    onImagesSelected(newFiles);
  };

  const removeImage = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index);
    const newPreviews = previews.filter((_, i) => i !== index);
    
    URL.revokeObjectURL(previews[index]);
    
    setFiles(newFiles);
    setPreviews(newPreviews);
    onImagesSelected(newFiles);
  };

  return (
    <div className="space-y-4">
      {/* Upload Button */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors">
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*"
          onChange={handleFileSelect}
          className="hidden"
        />
        
        <button
          onClick={() => fileInputRef.current?.click()}
          className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Upload className="w-5 h-5 mr-2" />
          {angle ? `Upload ${angle} View` : 'Upload Images'}
        </button>
        
        <p className="mt-2 text-sm text-gray-500">
          {files.length}/{maxImages} images selected
        </p>
      </div>

      {/* Image Previews */}
      {previews.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {previews.map((preview, index) => (
            <div key={index} className="relative group">
              <img
                src={preview}
                alt={`Preview ${index + 1}`}
                className="w-full h-48 object-cover rounded-lg"
              />
              <button
                onClick={() => removeImage(index)}
                className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X className="w-4 h-4" />
              </button>
              <div className="absolute bottom-2 left-2 px-2 py-1 bg-black bg-opacity-50 text-white text-xs rounded">
                Image {index + 1}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
