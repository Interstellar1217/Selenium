document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    
    // 示例：添加一个事件监听器
    document.querySelector('.container').addEventListener('click', function(event) {
        console.log('Container clicked:', event);
    });
});