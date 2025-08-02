import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Header from './components/Header';
import FileSection from './components/FileSection';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';
import './App.css';

function App() {
    const [blobs, setBlobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [comments, setComments] = useState({});

    useEffect(() => {
        fetchBlobs();
    }, []);

    const fetchBlobs = async () => {
        try {
            setLoading(true);
            const response = await axios.get('/api/blobs');
            setBlobs(response.data);
            setError(null);
        } catch (err) {
            setError('Failed to load files. Please check your connection and try again.');
            console.error('Error fetching blobs:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleCommentChange = (blobName, value) => {
        setComments(prev => ({
            ...prev,
            [blobName]: value
        }));
    };

    const handleSaveComment = async (blobName) => {
        try {
            await axios.post('/api/comments', {
                filename: blobName,
                comment: comments[blobName]
            });
            
            // Show success message
            const event = new CustomEvent('showNotification', {
                detail: {
                    type: 'success',
                    message: `Comment saved for ${blobName.split('/').pop()}`
                }
            });
            window.dispatchEvent(event);
        } catch (err) {
            console.error('Error saving comment:', err);
            const event = new CustomEvent('showNotification', {
                detail: {
                    type: 'error',
                    message: 'Failed to save comment. Please try again.'
                }
            });
            window.dispatchEvent(event);
        }
    };

    const groupByPrefix = (prefix) =>
        blobs.filter(blob => blob.name.startsWith(prefix));

    const sections = [
        {
            title: "AI Predictions",
            icon: "🤖",
            items: groupByPrefix("predictions/"),
            description: "AI-generated analysis and predictions for heart sound recordings"
        },
        {
            title: "Heart Sound Recordings",
            icon: "🫀",
            items: groupByPrefix("recordings/"),
            description: "Raw audio recordings of heart sounds for analysis",
            showWaveform: true
        },
        {
            title: "Embeddings",
            icon: "📊",
            items: groupByPrefix("embeddings/"),
            description: "Feature embeddings extracted from audio recordings"
        },
        {
            title: "Metadata",
            icon: "📋",
            items: groupByPrefix("metadata/"),
            description: "Additional information and metadata for recordings"
        }
    ];

    if (loading) {
        return (
            <div className="app">
                <Header />
                <main className="main-content">
                    <LoadingSpinner message="Loading clinical data..." />
                </main>
            </div>
        );
    }

    if (error) {
        return (
            <div className="app">
                <Header />
                <main className="main-content">
                    <ErrorMessage message={error} onRetry={fetchBlobs} />
                </main>
            </div>
        );
    }

    return (
        <div className="app">
            <Header />
            <main className="main-content">
                <div className="container">
                    <div className="intro-section">
                        <h1>Clinical Data Management</h1>
                        <p>
                            Welcome to the RED-RHD Clinical Interface. This platform provides 
                            comprehensive tools for managing heart sound recordings, AI predictions, 
                            and clinical metadata. Use the sections below to review, analyze, and 
                            annotate your clinical data.
                        </p>
                        <div className="stats-grid">
                            <div className="stat-card">
                                <div className="stat-number">{blobs.length}</div>
                                <div className="stat-label">Total Files</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-number">{groupByPrefix("recordings/").length}</div>
                                <div className="stat-label">Recordings</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-number">{groupByPrefix("predictions/").length}</div>
                                <div className="stat-label">Predictions</div>
                            </div>
                        </div>
                    </div>

                    {sections.map((section, index) => (
                        <FileSection
                            key={index}
                            title={section.title}
                            icon={section.icon}
                            items={section.items}
                            description={section.description}
                            showWaveform={section.showWaveform}
                            comments={comments}
                            onCommentChange={handleCommentChange}
                            onSaveComment={handleSaveComment}
                        />
                    ))}
                </div>
            </main>
        </div>
    );
}

export default App;