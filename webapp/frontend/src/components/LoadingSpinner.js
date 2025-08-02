import React from 'react';
import { Loader2 } from 'lucide-react';
import './LoadingSpinner.css';

const LoadingSpinner = ({ message = "Loading..." }) => {
    return (
        <div className="loading-container">
            <div className="loading-content">
                <Loader2 className="loading-icon" />
                <p className="loading-message">{message}</p>
            </div>
        </div>
    );
};

export default LoadingSpinner;