import React, { useEffect, useState, useRef } from 'react';
import WaveSurfer from 'wavesurfer.js';

function App() {
    const [blobs, setBlobs] = useState([]);
    const [comments, setComments] = useState({});
    const waveSurferRefs = useRef({}); // store WaveSurfer instances

    useEffect(() => {
        fetch('/api/blobs')
            .then((res) => res.json())
            .then((data) => setBlobs(data));
    }, []);

    const handleCommentChange = (blobName, value) => {
        setComments(prev => ({
            ...prev,
            [blobName]: value
        }));
    };

    const handleSaveComment = (blobName) => {
        console.log(`Saved comment for ${blobName}:`, comments[blobName]);
        alert(`Saved comment for:\n${blobName}\n\n"${comments[blobName]}"`);
    };

    const initWaveform = (blobName, url) => {
        if (waveSurferRefs.current[blobName]) return; // prevent duplicates
        const container = document.querySelector(`#waveform-${blobName.replace(/[^\w]/g, '_')}`);
        const ws = WaveSurfer.create({
            container,
            waveColor: '#90caf9',
            progressColor: '#1976d2',
            height: 120,
            responsive: true,
            scrollParent: true,
            minPxPerSec: 100,
            normalize: true
        });
        ws.load(url);
        waveSurferRefs.current[blobName] = ws;

        // === Controls Container ===
        const controlsContainer = document.createElement("div");
        controlsContainer.style.marginTop = "10px";

        // Play/Pause button
        const playPauseBtn = document.createElement("button");
        playPauseBtn.innerText = "Play Recording";
        playPauseBtn.onclick = () => {
            ws.playPause();
            playPauseBtn.innerText = ws.isPlaying() ? "Pause" : "Play";
        };

        // Seek slider
        const seekSlider = document.createElement("input");
        seekSlider.type = "range";
        seekSlider.min = 0;
        seekSlider.max = 100;
        seekSlider.value = 0;
        seekSlider.style.width = "300px";
        seekSlider.oninput = (e) => {
            const progress = e.target.value / 100;
            ws.seekTo(progress);
        };

        // Update slider as audio plays
        ws.on('audioprocess', () => {
            if (ws.isPlaying()) {
                seekSlider.value = (ws.getCurrentTime() / ws.getDuration()) * 100;
            }
        });

        // Zoom slider
        const zoomLabel = document.createElement("label");
        zoomLabel.innerText = " Zoom: ";
        const zoomSlider = document.createElement("input");
        zoomSlider.type = "range";
        zoomSlider.min = 20;
        zoomSlider.max = 500;
        zoomSlider.value = 100;
        zoomSlider.step = 10;
        zoomSlider.oninput = (e) => ws.zoom(Number(e.target.value));

        // Append controls
        controlsContainer.appendChild(playPauseBtn);
        controlsContainer.appendChild(seekSlider);
        controlsContainer.appendChild(zoomLabel);
        controlsContainer.appendChild(zoomSlider);

        container.parentElement.insertBefore(controlsContainer, container.nextSibling);
    };



    const groupByPrefix = (prefix) =>
        blobs.filter(blob => blob.name.startsWith(prefix));
    const others = blobs.filter(blob =>
        !["predictions/", "recordings/", "embeddings/", "metadata/"].some(p => blob.name.startsWith(p))
    );

    const renderSection = (title, items) => (
        <>
            <h2>{title}</h2>
            {items.length === 0 ? (
                <p><i>No files found in this section.</i></p>
            ) : (
                <ul>
                    {items.map((blob, i) => (
                        <li key={i} style={{ marginBottom: '30px' }}>
                            <a href={blob.url} target="_blank" rel="noopener noreferrer">
                                {blob.name}
                            </a>
                            {title === " Recordings" && (
                                <div>
                                    <div
                                        id={`waveform-${blob.name.replace(/[^\w]/g, '_')}`}
                                        style={{ width: '500px', marginTop: '10px' }}
                                    ></div>
                                    <button onClick={() => initWaveform(blob.name, blob.url)}>Load Waveform</button>
                                </div>
                            )}
                            <br />
                            <textarea
                                rows="2"
                                cols="60"
                                placeholder="Doctor Feedback: Write a comment..."
                                value={comments[blob.name] || ''}
                                onChange={e => handleCommentChange(blob.name, e.target.value)}
                            />
                            <br />
                            <button onClick={() => handleSaveComment(blob.name)}>Save Comment</button>
                        </li>
                    ))}
                </ul>
            )}
        </>
    );

    return (
        <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
            <h1>RED-RHD Clinical Interface</h1>
            <p>Welcome to the RED-RHD Clinical Interface. Here you can view and manage heart sound recordings, AI predictions, and metadata.</p>
            {renderSection(" Predictions", groupByPrefix("predictions/"))}
            {renderSection(" Recordings", groupByPrefix("recordings/"))}
        </div>
    );
}

export default App;
