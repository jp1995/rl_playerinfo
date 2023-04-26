document.addEventListener('DOMContentLoaded', function() {

    //  Doesn't work on template update atm
    let titletransition = document.querySelector(".title");
    setTimeout(function() {
        titletransition.classList.add("visible");
    }, 100);

    const socket = io.connect('/');

    socket.on("connect",() => {
        // the update loop is started
        socket.emit('request_mmr');
        socket.emit('request_match')
        socket.emit('request_playlist')
    })

    socket.on('reply_mmr_update', function(data) {
        console.log(data)
        let mmrtable = document.querySelector('.mmrtable');
        mmrtable.innerHTML = data.html;
    });

    socket.on('reply_match_update', function(data) {
        console.log(data)
        let match = document.querySelector('.trackertable');
        match.innerHTML = data.html;
    });

    socket.on('reply_playlist_update', function(data) {
        console.log(data)
        let playlist = document.querySelector('.title');
        playlist.innerHTML = data.html;
    });

    // refresh doesn't break the site
    socket.emit("rq_current_playlist");
    socket.emit("rq_current_mmr");
    socket.emit("rq_current_match");
});