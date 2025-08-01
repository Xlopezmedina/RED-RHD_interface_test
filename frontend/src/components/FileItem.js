import React, { useState, useRef, useEffect } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { Play, Pause, Download, MessageSquare, Save, Volume2 } from 'lucide-react';
import './FileItem.css';

const FileItem = ({ item, showWaveform, comment, onCommentChange, onSaveComment }) => {
    const [isPlaying, setIsPlaying] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [waveformLoaded, setWaveformLoaded] = useState(false);
    const [duration, setDuration] = useState(0);
    const [currentTime, setCurrentTime] = useState(0);
    const waveformRef = useRef(null);
    const waveSurferRef = useRef(null);

    const fileName = item.name.split('/').pop();
    const fileSize = item.size ? `${(item.size / 1024).toFixed(1)} KB` : 'Unknown size';
    const lastModified = item.last_modified ? 
        new Date(item.last_modified).toLocaleDateString() : 'Unknown date';

    useEffect(() => {
        return () => {
            if (waveSurferRef.current) {
                waveSurferRef.current.destroy();
            }
        };
    }, []);

    const initWaveform = async () => {
        if (waveSurferRef.current || !waveformRef.current) return;

        setIsLoading(true);
        try {
            const waveSurfer = WaveSurfer.create({
                container: waveformRef.current,
                waveColor: '#94a3b8',
                progressColor: '#3b82f6',
                cursorColor: '#1e293b',
                height: 80,
                responsive: true,
                normalize: true,
                backend: 'WebAudio',
                cors: 'anonymous'
            });

            waveSurfer.on('ready', () => {
                setWaveformLoaded(true);
                setDuration(waveSurfer.getDuration());
                setIsLoading(false);
            });

            waveSurfer.on('play', () => setIsPlaying(true));
            waveSurfer.on('pause', () => setIsPlaying(false));
            
            waveSurfer.on('audioprocess', () => {
                setCurrentTime(waveSurfer.getCurrentTime());
            });

            waveSurfer.on('error', (error) => {
                console.error('WaveSurfer error:', error);
                setIsLoading(false);
                // Try to load with MediaElement backend as fallback
                if (waveSurfer.backend === 'WebAudio') {
                    console.log('Retrying with MediaElement backend...');
                    waveSurfer.destroy();
                    initWaveformFallback();
                }
            });

            console.log('Loading audio from:', item.url);
            waveSurfer.load(item.url);
            waveSurferRef.current = waveSurfer;
        } catch (error) {
            console.error('Error initializing waveform:', error);
            setIsLoading(false);
        }
    };

    const initWaveformFallback = async () => {
        if (!waveformRef.current) return;

        try {
            const waveSurfer = WaveSurfer.create({
                container: waveformRef.current,
                waveColor: '#94a3b8',
                progressColor: '#3b82f6',
                cursorColor: '#1e293b',
                height: 80,
                responsive: true,
                normalize: true,
                backend: 'MediaElement'
            });

            waveSurfer.on('ready', () => {
                setWaveformLoaded(true);
                setDuration(waveSurfer.getDuration());
                setIsLoading(false);
            });

            waveSurfer.on('play', () => setIsPlaying(true));
            waveSurfer.on('pause', () => setIsPlaying(false));
            
            waveSurfer.on('audioprocess', () => {
                setCurrentTime(waveSurfer.getCurrentTime());
            });

            waveSurfer.on('error', (error) => {
                console.error('WaveSurfer fallback error:', error);
                setIsLoading(false);
            });

            waveSurfer.load(item.url);
            waveSurferRef.current = waveSurfer;
        } catch (error) {
            console.error('Error initializing fallback waveform:', error);
            setIsLoading(false);
        }
    };

    const togglePlayPause = () => {
        if (waveSurferRef.current) {
            waveSurferRef.current.playPause();
        }
    };

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div className="file-item">
            <div className="file-header">
                <div className="file-info">
                    <h3 className="file-name">{fileName}</h3>
                    <div className="file-meta">
                        <span>{fileSize}</span>
                        <span>•</span>
                        <span>{lastModified}</span>
                    </div>
                </div>
                <div className="file-actions">
                    <a 
                        href={`http://localhost:5000/api/download/${item.name}`}
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="btn btn-secondary"
                        title="Download file"
                        download
                    >
                        <Download size={16} />
                    </a>
                </div>
            </div>

            {showWaveform && (
                <div className="audio-section">
                    {!waveformLoaded && (
                        <button 
                            onClick={initWaveform}
                            className="btn btn-primary load-waveform-btn"
                            disabled={isLoading}
                        >
                            <Volume2 size={16} />
                            {isLoading ? 'Loading...' : 'Load Audio Waveform'}
                        </button>
                    )}
                    
                    {waveformLoaded && (
                        <div className="audio-controls">
                            <div className="waveform-container">
                                <div ref={waveformRef} className="waveform"></div>
                            </div>
                            <div className="playback-controls">
                                <button 
                                    onClick={togglePlayPause}
                                    className="btn btn-primary play-btn"
                                >
                                    {isPlaying ? <Pause size={16} /> : <Play size={16} />}
                                    {isPlaying ? 'Pause' : 'Play'}
                                </button>
                                <div className="time-display">
                                    {formatTime(currentTime)} / {formatTime(duration)}
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}

            <div className="comment-section">
                <div className="comment-header">
                    <MessageSquare size={16} />
                    <label className="form-label">Clinical Notes</label>
                </div>
                <textarea
                    className="form-textarea comment-textarea"
                    placeholder="Add your clinical observations, findings, or notes about this file..."
                    value={comment}
                    onChange={(e) => onCommentChange(e.target.value)}
                    rows={3}
                />
                <button 
                    onClick={onSaveComment}
                    className="btn btn-success save-comment-btn"
                    disabled={!comment.trim()}
                >
                    <Save size={16} />
                    Save Notes
                </button>
            </div>
        </div>
    );
};

export default FileItem;