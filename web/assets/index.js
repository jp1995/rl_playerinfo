$(function() {

    //  Doesn't work on template update atm
    let titletransition = document.querySelector(".title");
    setTimeout(function() {
        titletransition.classList.add("visible");
    }, 100);

    const socket = io.connect('http://localhost:5000');

    socket.on("connect",() => {
        // the update loop is started
        socket.emit('request_mmr');
        socket.emit('request_match')
        socket.emit('request_playlist')
    })

    socket.on('reply_mmr_update', function(data) {
        console.log(data)
        $('.mmrtable').html(data.html);
    });

    socket.on('reply_match_update', function(data) {
        console.log(data)
        $('.trackertable').html(data.html);
    });

    socket.on('reply_playlist_update', function(data) {
        console.log(data)
        $('.title').html(data.html);
    });

    // refresh doesn't break the site
    socket.emit("rq_current_playlist");
    socket.emit("rq_current_mmr");
    socket.emit("rq_current_match");
});