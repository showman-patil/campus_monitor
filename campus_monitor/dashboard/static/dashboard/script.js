// Global utility functions for the Campus Monitor application

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);
    
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
    return date.toLocaleDateString();
}

function getConfidenceBadgeClass(confidence) {
    if (confidence > 0.9) return 'bg-green-500';
    if (confidence > 0.7) return 'bg-yellow-500';
    return 'bg-red-500';
}

// Cache control - prevent browser caching
if (window.performance && window.performance.navigation.type === 1) {
    console.log('Page reloaded');
}
