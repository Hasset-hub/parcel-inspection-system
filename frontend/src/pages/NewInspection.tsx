import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MultiAngleCapture from '../components/inspection/MultiAngleCapture';
import api from '../services/api';

const NewInspection = () => {
  const [step, setStep] = useState<'parcel' | 'images' | 'processing'>('parcel');
  const [trackingNumber, setTrackingNumber] = useState('');
  const [images, setImages] = useState<{ [key: string]: File[] }>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleStartInspection = async () => {
    if (!trackingNumber) {
      setError('Please enter tracking number');
      return;
    }
    setError('');
    setStep('images');
  };

  const handleImagesCollected = (collectedImages: { [key: string]: File[] }) => {
    setImages(collectedImages);
  };

  const handleSubmitInspection = async () => {
    setLoading(true);
    setError('');

    try {
      // Count total images
      const totalImages = Object.values(images).reduce((sum, files) => sum + files.length, 0);
      
      if (totalImages === 0) {
        setError('Please upload at least one image');
        setLoading(false);
        return;
      }

      setStep('processing');

      // For demo: Just process images with ML endpoint
      const results = [];
      
      for (const [angle, files] of Object.entries(images)) {
        for (const file of files) {
          const formData = new FormData();
          formData.append('file', file);

          try {
            const response = await api.post('/api/v1/ml/detect-damage', formData, {
              headers: { 'Content-Type': 'multipart/form-data' }
            });
            
            results.push({
              angle,
              filename: file.name,
              result: response.data
            });
          } catch (err) {
            console.error('Failed to process image:', err);
          }
        }
      }

      // Show results
      alert(`Inspection Complete!\n\nProcessed ${totalImages} images\nDamaged: ${results.filter(r => r.result.has_damage).length}`);
      
      navigate('/inspections');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit inspection');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">New Inspection</h1>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-center space-x-4">
          <div className={`flex items-center ${step === 'parcel' ? 'text-blue-600' : 'text-green-600'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              step === 'parcel' ? 'bg-blue-600 text-white' : 'bg-green-600 text-white'
            }`}>
              1
            </div>
            <span className="ml-2 font-medium">Parcel Info</span>
          </div>
          <div className="w-16 h-1 bg-gray-300" />
          <div className={`flex items-center ${step === 'images' ? 'text-blue-600' : step === 'processing' ? 'text-green-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              step === 'images' ? 'bg-blue-600 text-white' : step === 'processing' ? 'bg-green-600 text-white' : 'bg-gray-300'
            }`}>
              2
            </div>
            <span className="ml-2 font-medium">Capture Images</span>
          </div>
          <div className="w-16 h-1 bg-gray-300" />
          <div className={`flex items-center ${step === 'processing' ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              step === 'processing' ? 'bg-blue-600 text-white' : 'bg-gray-300'
            }`}>
              3
            </div>
            <span className="ml-2 font-medium">Processing</span>
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Step 1: Parcel Info */}
      {step === 'parcel' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Parcel Information</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tracking Number *
              </label>
              <input
                type="text"
                value={trackingNumber}
                onChange={(e) => setTrackingNumber(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Enter tracking number"
              />
            </div>

            <button
              onClick={handleStartInspection}
              className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Start Inspection →
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Image Capture */}
      {step === 'images' && (
        <div>
          <MultiAngleCapture onImagesCollected={handleImagesCollected} />
          
          <div className="mt-6 flex justify-between">
            <button
              onClick={() => setStep('parcel')}
              className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              ← Back
            </button>
            <button
              onClick={handleSubmitInspection}
              disabled={loading || Object.values(images).flat().length === 0}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? 'Processing...' : 'Submit Inspection ✓'}
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Processing */}
      {step === 'processing' && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h3 className="text-xl font-semibold mb-2">Processing Images...</h3>
          <p className="text-gray-600">Running AI damage detection on uploaded images</p>
        </div>
      )}
    </div>
  );
};

export default NewInspection;
