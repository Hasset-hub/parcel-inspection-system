import { useState } from 'react';
import ImageUpload from './ImageUpload';

const ANGLES = [
  { id: 'front', label: 'Front View', icon: '⬆️' },
  { id: 'back', label: 'Back View', icon: '⬇️' },
  { id: 'left', label: 'Left View', icon: '⬅️' },
  { id: 'right', label: 'Right View', icon: '➡️' },
  { id: 'top', label: 'Top View', icon: '⬆️' },
  { id: 'bottom', label: 'Bottom View', icon: '⬇️' },
];

interface MultiAngleCaptureProps {
  onImagesCollected: (images: { [key: string]: File[] }) => void;
}

const MultiAngleCapture = ({ onImagesCollected }: MultiAngleCaptureProps) => {
  const [currentAngle, setCurrentAngle] = useState(0);
  const [collectedImages, setCollectedImages] = useState<{ [key: string]: File[] }>({});

  const handleImagesForAngle = (files: File[]) => {
    const angle = ANGLES[currentAngle].id;
    const updated = { ...collectedImages, [angle]: files };
    setCollectedImages(updated);
    onImagesCollected(updated);
  };

  const nextAngle = () => {
    if (currentAngle < ANGLES.length - 1) {
      setCurrentAngle(currentAngle + 1);
    }
  };

  const prevAngle = () => {
    if (currentAngle > 0) {
      setCurrentAngle(currentAngle - 1);
    }
  };

  const totalImages = Object.values(collectedImages).reduce((sum, files) => sum + files.length, 0);

  return (
    <div className="space-y-6">
      {/* Progress */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            Angle {currentAngle + 1} of {ANGLES.length}
          </span>
          <span className="text-sm text-gray-500">
            {totalImages} total images
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${((currentAngle + 1) / ANGLES.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Angle Selector */}
      <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
        {ANGLES.map((angle, index) => (
          <button
            key={angle.id}
            onClick={() => setCurrentAngle(index)}
            className={`p-3 rounded-lg text-center transition-colors ${
              currentAngle === index
                ? 'bg-blue-600 text-white'
                : collectedImages[angle.id]?.length > 0
                ? 'bg-green-100 text-green-700 border-2 border-green-500'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <div className="text-2xl mb-1">{angle.icon}</div>
            <div className="text-xs font-medium">{angle.label}</div>
            {collectedImages[angle.id]?.length > 0 && (
              <div className="text-xs mt-1">
                {collectedImages[angle.id].length} ✓
              </div>
            )}
          </button>
        ))}
      </div>

      {/* Current Angle Upload */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <span className="text-3xl mr-3">{ANGLES[currentAngle].icon}</span>
          {ANGLES[currentAngle].label}
        </h3>
        
        <ImageUpload
          angle={ANGLES[currentAngle].label}
          onImagesSelected={handleImagesForAngle}
          maxImages={2}
        />

        {/* Navigation */}
        <div className="flex justify-between mt-6">
          <button
            onClick={prevAngle}
            disabled={currentAngle === 0}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ← Previous
          </button>
          <button
            onClick={nextAngle}
            disabled={currentAngle === ANGLES.length - 1}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  );
};

export default MultiAngleCapture;
