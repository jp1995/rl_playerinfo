$(function() {

    let titletransition = document.querySelector(".title");
    setTimeout(function() {
        titletransition.classList.add("visible");
    }, 100);

    function updateMMR() {
        $.ajax({
            url: '/update_mmr',
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                $('.mmrtable').html(data.html);
            }
        });
    }

    function updatePlaylist() {
        $.ajax({
            url: '/update_playlist',
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                $('.title').html(data.html);
            }
        });
    }

    function updateMatch() {
        $.ajax({
            url: '/update_match',
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                $('.trackertable').html(data.html);
            }
        });
    }

    updateMMR();
    updateMatch();
    updatePlaylist();

});