// toggle-menu.js - ハンバーガーメニューの動作制御（改善版）

document.addEventListener('DOMContentLoaded', function() {
    // ハンバーガーメニューボタンの取得
    const toggleButton = document.querySelector('.toggle-menu-button');
    // ナビゲーションメニューの取得
    const siteMenu = document.querySelector('.header-site-menu');
    
    // エラーハンドリング：要素が見つからない場合
    if (!toggleButton) {
        console.error('ハンバーガーメニューボタンが見つかりません (.toggle-menu-button)');
        return;
    }
    
    if (!siteMenu) {
        console.error('サイトメニューが見つかりません (.header-site-menu)');
        return;
    }
    
    // メニューの初期状態
    let isMenuOpen = false;
    
    // ARIA属性の初期設定
    toggleButton.setAttribute('aria-expanded', 'false');
    toggleButton.setAttribute('aria-controls', 'header-site-menu');
    siteMenu.setAttribute('aria-hidden', 'true');
    siteMenu.setAttribute('id', 'header-site-menu');
    
    // フォーカストラップ用の要素取得
    const focusableElements = siteMenu.querySelectorAll(
        'a[href], button:not([disabled]), textarea:not([disabled]), input[type="text"]:not([disabled]), input[type="radio"]:not([disabled]), input[type="checkbox"]:not([disabled]), select:not([disabled])'
    );
    const firstFocusableElement = focusableElements[0];
    const lastFocusableElement = focusableElements[focusableElements.length - 1];
    
    // メニューを開く関数
    function openMenu() {
        isMenuOpen = true;
        siteMenu.classList.add('menu-open');
        toggleButton.classList.add('menu-active');
        toggleButton.setAttribute('aria-expanded', 'true');
        toggleButton.setAttribute('aria-label', 'メニューを閉じる');
        siteMenu.setAttribute('aria-hidden', 'false');
        
        // ボディのスクロールを無効化（モバイル対応）
        document.body.style.overflow = 'hidden';
        
        // フォーカスを最初の要素に移動
        if (firstFocusableElement) {
            firstFocusableElement.focus();
        }
        
        console.log('メニューを開きました');
    }
    
    // メニューを閉じる関数
    function closeMenu() {
        isMenuOpen = false;
        siteMenu.classList.remove('menu-open');
        toggleButton.classList.remove('menu-active');
        toggleButton.setAttribute('aria-expanded', 'false');
        toggleButton.setAttribute('aria-label', 'メニューを開く');
        siteMenu.setAttribute('aria-hidden', 'true');
        
        // ボディのスクロールを復元
        document.body.style.overflow = '';
        
        // フォーカスをボタンに戻す
        toggleButton.focus();
        
        console.log('メニューを閉じました');
    }
    
    // ハンバーガーメニューボタンのクリックイベント
    toggleButton.addEventListener('click', function(e) {
        e.preventDefault();
        
        if (isMenuOpen) {
            closeMenu();
        } else {
            openMenu();
        }
    });
    
    // ESCキーでメニューを閉じる
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isMenuOpen) {
            closeMenu();
        }
        
        // メニューが開いているときのTab循環制御
        if (isMenuOpen && e.key === 'Tab') {
            if (e.shiftKey) {
                // Shift + Tab（逆方向）
                if (document.activeElement === firstFocusableElement) {
                    e.preventDefault();
                    lastFocusableElement.focus();
                }
            } else {
                // Tab（順方向）
                if (document.activeElement === lastFocusableElement) {
                    e.preventDefault();
                    firstFocusableElement.focus();
                }
            }
        }
    });
    
    // 画面サイズが変更されたときの処理
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            // デスクトップサイズ以上でメニューが開いている場合は閉じる
            if (window.innerWidth >= 801 && isMenuOpen) {
                closeMenu();
                console.log('画面サイズ変更でメニューを閉じました');
            }
        }, 250);
    });
    
    // メニュー外をクリックしたときにメニューを閉じる
    document.addEventListener('click', function(e) {
        // クリックされた要素がメニュー内でもボタンでもない場合
        if (isMenuOpen && 
            !siteMenu.contains(e.target) && 
            !toggleButton.contains(e.target)) {
            closeMenu();
            console.log('メニュー外クリックでメニューを閉じました');
        }
    });
    
    // メニュー内のリンクがクリックされたときにメニューを閉じる
    const menuLinks = siteMenu.querySelectorAll('a');
    menuLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            if (isMenuOpen) {
                // 少し遅延させてスムーズな遷移を実現
                setTimeout(closeMenu, 100);
            }
        });
    });
    
    // タッチイベントの処理（スワイプでメニューを閉じる）
    let touchStartY = 0;
    let touchStartX = 0;
    
    siteMenu.addEventListener('touchstart', function(e) {
        touchStartY = e.touches[0].clientY;
        touchStartX = e.touches[0].clientX;
    }, { passive: true });
    
    siteMenu.addEventListener('touchend', function(e) {
        if (!isMenuOpen) return;
        
        const touchEndY = e.changedTouches[0].clientY;
        const touchEndX = e.changedTouches[0].clientX;
        const deltaY = touchStartY - touchEndY;
        const deltaX = touchStartX - touchEndX;
        
        // 上方向へのスワイプでメニューを閉じる
        if (deltaY > 50 && Math.abs(deltaX) < 100) {
            closeMenu();
            console.log('上方向スワイプでメニューを閉じました');
        }
    }, { passive: true });
    
    // 初期化完了メッセージ
    console.log('ハンバーガーメニューが初期化されました（改善版）');
    
    // パフォーマンス測定
    if (window.performance && window.performance.mark) {
        window.performance.mark('menu-initialization-complete');
    }
});