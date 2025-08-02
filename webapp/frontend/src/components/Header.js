import React from 'react';
import { Heart, Activity } from 'lucide-react';
import './Header.css';

const Header = () => {
    return (
        <header className="header">
            <div className="header-container">
                <div className="header-brand">
                    <div className="brand-icon">
                        <Heart className="heart-icon" />
                        <Activity className="activity-icon" />
                    </div>
                    <div className="brand-text">
                        <h1>RED-RHD</h1>
                        <span>Clinical Interface</span>
                    </div>
                </div>
                <nav className="header-nav">
                    <a href="#recordings" className="nav-link">Recordings</a>
                    <a href="#predictions" className="nav-link">Predictions</a>
                    <a href="#analytics" className="nav-link">Analytics</a>
                </nav>
            </div>
        </header>
    );
};

export default Header;