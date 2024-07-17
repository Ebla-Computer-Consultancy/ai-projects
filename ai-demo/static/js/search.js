$(document).ready(() => {
    setTimeout(() => {
        $('html , body').animate({
            scrollTop: $('.hero-section').height()
        }, 100)
    }, 100)
})