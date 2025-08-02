import React from 'react';
import FileItem from './FileItem';
import './FileSection.css';

const FileSection = ({ 
    title, 
    icon, 
    items, 
    description, 
    showWaveform, 
    comments, 
    onCommentChange, 
    onSaveComment 
}) => {
    return (
        <section className="file-section">
            <div className="section-header">
                <div className="section-title">
                    <span className="section-icon">{icon}</span>
                    <h2>{title}</h2>
                    <span className="item-count">({items.length})</span>
                </div>
                <p className="section-description">{description}</p>
            </div>
            
            <div className="section-content">
                {items.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-icon">{icon}</div>
                        <h3>No files found</h3>
                        <p>There are currently no files in this section.</p>
                    </div>
                ) : (
                    <div className="file-grid">
                        {items.map((item, index) => (
                            <FileItem
                                key={index}
                                item={item}
                                showWaveform={showWaveform}
                                comment={comments[item.name] || ''}
                                onCommentChange={(value) => onCommentChange(item.name, value)}
                                onSaveComment={() => onSaveComment(item.name)}
                            />
                        ))}
                    </div>
                )}
            </div>
        </section>
    );
};

export default FileSection;