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

// Accessibility: close dropdowns with Escape and manage ARIA-expanded
(function(){
    const datasetsBtn = document.getElementById('datasets-btn');
    const datasetsMenu = document.getElementById('datasets-menu');
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');

    function closeDatasets(){
        if(datasetsMenu && !datasetsMenu.classList.contains('hidden')){
            datasetsMenu.classList.add('hidden');
            if(datasetsBtn) datasetsBtn.setAttribute('aria-expanded','false');
        }
    }

    document.addEventListener('keydown', function(e){
        if(e.key === 'Escape'){
            closeDatasets();
            if(navMenu && !navMenu.classList.contains('hidden')) navMenu.classList.add('hidden');
        }
    });

    if(datasetsBtn && datasetsMenu){
        const items = Array.from(datasetsMenu.querySelectorAll('.dataset-item'));

        function openDatasets(){
            datasetsMenu.classList.remove('hidden');
            datasetsMenu.classList.add('show');
            datasetsBtn.setAttribute('aria-expanded','true');
            const caret = datasetsBtn.querySelector('.datasets-caret');
            if(caret) caret.style.transform = 'rotate(180deg)';
        }
        function hideDatasets(){
            datasetsMenu.classList.add('hidden');
            datasetsMenu.classList.remove('show');
            datasetsBtn.setAttribute('aria-expanded','false');
            const caret = datasetsBtn.querySelector('.datasets-caret');
            if(caret) caret.style.transform = 'rotate(0deg)';
        }

        datasetsBtn.addEventListener('click', function(e){
            e.preventDefault();
            const open = !datasetsMenu.classList.contains('hidden');
            if(open) hideDatasets(); else openDatasets();
        });

        // keyboard open via Enter/Space, and arrow navigation when open
        datasetsBtn.addEventListener('keydown', function(e){
            if(e.key === 'Enter' || e.key === ' '){
                e.preventDefault();
                const open = !datasetsMenu.classList.contains('hidden');
                if(open) hideDatasets(); else { openDatasets(); if(items[0]) items[0].focus(); }
            } else if(e.key === 'ArrowDown'){
                e.preventDefault(); openDatasets(); if(items[0]) items[0].focus();
            } else if(e.key === 'ArrowUp'){
                e.preventDefault(); openDatasets(); if(items[items.length-1]) items[items.length-1].focus();
            }
        });

        // Manage arrow navigation inside menu
        items.forEach((itm, idx) => {
            itm.addEventListener('keydown', function(e){
                if(e.key === 'ArrowDown'){
                    e.preventDefault();
                    const next = items[(idx + 1) % items.length]; if(next) next.focus();
                } else if(e.key === 'ArrowUp'){
                    e.preventDefault();
                    const prev = items[(idx - 1 + items.length) % items.length]; if(prev) prev.focus();
                } else if(e.key === 'Escape'){
                    hideDatasets(); datasetsBtn.focus();
                }
            });
        });
        // close when clicking outside — hide with animation classes
        document.addEventListener('click', function(e){
            if(!datasetsBtn.contains(e.target) && datasetsMenu && !datasetsMenu.contains(e.target)){
                hideDatasets();
            }
        });
    }

    // 'More' menu handling (new consolidated menu)
    const moreBtn = document.getElementById('more-btn');
    const moreMenu = document.getElementById('more-menu');
    if(moreBtn && moreMenu){
        const moreItems = Array.from(moreMenu.querySelectorAll('.more-item'));
        function openMore(){
            moreMenu.classList.remove('hidden'); moreMenu.classList.add('show');
            moreBtn.setAttribute('aria-expanded','true');
            const caret = moreBtn.querySelector('.more-caret'); if(caret) caret.style.transform = 'rotate(180deg)';
        }
        function hideMore(){
            moreMenu.classList.add('hidden'); moreMenu.classList.remove('show');
            moreBtn.setAttribute('aria-expanded','false');
            const caret = moreBtn.querySelector('.more-caret'); if(caret) caret.style.transform = 'rotate(0deg)';
        }

        moreBtn.addEventListener('click', function(e){ e.preventDefault(); const open = !moreMenu.classList.contains('hidden'); if(open) hideMore(); else openMore(); });
        moreBtn.addEventListener('keydown', function(e){
            if(e.key === 'Enter' || e.key === ' '){ e.preventDefault(); const open = !moreMenu.classList.contains('hidden'); if(open) hideMore(); else { openMore(); if(moreItems[0]) moreItems[0].focus(); } }
            else if(e.key === 'ArrowDown'){ e.preventDefault(); openMore(); if(moreItems[0]) moreItems[0].focus(); }
            else if(e.key === 'ArrowUp'){ e.preventDefault(); openMore(); if(moreItems[moreItems.length-1]) moreItems[moreItems.length-1].focus(); }
        });
        moreItems.forEach((it, idx) => {
            it.addEventListener('keydown', function(e){
                if(e.key === 'ArrowDown'){ e.preventDefault(); const next = moreItems[(idx+1)%moreItems.length]; if(next) next.focus(); }
                else if(e.key === 'ArrowUp'){ e.preventDefault(); const prev = moreItems[(idx-1+moreItems.length)%moreItems.length]; if(prev) prev.focus(); }
                else if(e.key === 'Escape'){ hideMore(); moreBtn.focus(); }
            });
        });
        document.addEventListener('click', function(e){ if(!moreBtn.contains(e.target) && moreMenu && !moreMenu.contains(e.target)) hideMore(); });
    }

    if(navToggle && navMenu){
        navToggle.addEventListener('click', function(){
            const open = !navMenu.classList.contains('hidden');
            navMenu.classList.toggle('hidden');
            navToggle.setAttribute('aria-expanded', String(!open));
            // animate hamburger -> X
            if(navToggle.classList.contains('hamburger')){
                navToggle.classList.toggle('open', !open);
            }
        });
    }
})();
