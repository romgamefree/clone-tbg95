window.mobileAndTabletCheck = function() {
    let check = false;
    (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino|android|ipad|playbook|silk/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4))) check = true;})(navigator.userAgent||navigator.vendor||window.opera);
    return check;
};
function playGame(){
    var gamearena = document.querySelector("#game-display-area");
    gamearena.innerHTML = `<iframe id="game-element" class="w-full h-full mx-auto" allowfullscreen="" loading="lazy" allow="autoplay; fullscreen; camera; focus-without-user-activation *; monetization; gamepad; keyboard-map *; xr-spatial-tracking; clipboard-write" scrolling="no" sandbox="allow-forms allow-modals allow-orientation-lock allow-pointer-lock allow-popups allow-popups-to-escape-sandbox allow-presentation allow-scripts allow-same-origin allow-downloads" src="game.html" title="Game RetroBowl" style="overflow: hidden; width: 100%;"></iframe>`;
    var game_play_pc = document.querySelector("#play-game-cover-pc");
    game_play_pc.style.display = "none";
}
function playGameMobile(){
    var gamearena = document.querySelector("#game-display-area");
    gamearena.innerHTML = `<iframe id="game-element" class="w-full h-full mx-auto" allowfullscreen="" loading="lazy" allow="autoplay; fullscreen; camera; focus-without-user-activation *; monetization; gamepad; keyboard-map *; xr-spatial-tracking; clipboard-write" scrolling="no" sandbox="allow-forms allow-modals allow-orientation-lock allow-pointer-lock allow-popups allow-popups-to-escape-sandbox allow-presentation allow-scripts allow-same-origin allow-downloads" src="game.html" title="Game RetroBowl" style="overflow: hidden; width: 100%;"></iframe>`;
    var game_play_pc = document.querySelector("#play-game-cover");
    game_play_pc.style.display = "none";
    var tmp = document.querySelector('#game-card');
    if(tmp.classList.contains("fullcreen")){
    tmp.classList.remove("fullcreen");
    } else {
    tmp.classList.add("fullcreen");
    }
}
function open_fullscreen(){
    var tmp = document.querySelector('#game-card');
    if(tmp.classList.contains("fullcreen")){
    tmp.classList.remove("fullcreen");
    if(mobileAndTabletCheck() == true){
        document.querySelector("#share-button svg use").setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', "#fullscreenexit");
    } else {
        document.querySelector("#share-button svg use").setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', "#fullscreenopen");
    }
    
    if(document.querySelector("#play-game-cover") && mobileAndTabletCheck() == true){
        document.querySelector("#game-display-area").innerHTML = "";
        document.querySelector("#play-game-cover").style.display = "block";
    }
    } else {
    document.querySelector("#share-button svg use").setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', "#fullscreenexit");
    tmp.classList.add("fullcreen");
    }
}
function showSearch(){
var search_arena = document.querySelector('#search-area');
if(search_arena.style.display == "none"){
    search_arena.style.display = "block";
}
}
function hideSearch(){
var search_arena = document.querySelector('#search-area');
if(search_arena.style.display == "block"){
    search_arena.style.display = "none";
}
}
var listGame;
fetch("/data/all.json",{
headers: {
    'Content-Type': 'application/json',
    },
}).then(response => response.json())
.then(data => {
    listGame = data;
});
function liveSearch(){
    var x = document.getElementById("search_input_new").value;
    console.log(x);
    
    let html = "";
    if(x != ""){
    for (var j=0; j<listGame.length; j++) {
        if (listGame[j].title.toUpperCase().indexOf(x.toUpperCase()) >= 0) {
            var item = listGame[j];
            const htmlItem = `<a class="m-2 group w-full flex"  href="https://tbg95.github.io/${item.slug}/">
    <img alt="${item.title}" src="https://tbg95.github.io/${item.slug}/logo.png" width="94" height="94" decoding="async" data-nimg="1" class="game-icon-a game-icon-img w-[64px] h-[64px]" loading="lazy" style="color: transparent;">
    <div class="flex flex-col justify-center ml-4 text-black">
    <div class="text-xl font-bold font-torus mb-1">${item.title}</div>
    </div>
</a>`;

            html += htmlItem;
        }
    }
    }
    // const e = document.createElement('div');
    // e.className  = "grid is-4-tablet is-4-desktop is-6-widescreen is-6-fullhd is-7-ultrawide";
    // e.innerHTML = html;  
    // console.log(document.querySelector('.gird'));
    document.querySelector('.MobileHeader_searchResult__k3_Yl').innerHTML = html;
    // return -1;
}
function showMenu(){
var menuLeft = document.querySelector('#menuLeft');
if(menuLeft.style.display == "none"){
    menuLeft.style.display = "block";
    document.querySelector("#btnMenu svg use").setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', "#closeMenuIcon");

} else {
    menuLeft.style.display = "none";
    document.querySelector("#btnMenu svg use").setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', "#openMenuIcon");

}
}
function loadGA(){
    var  r = document.createElement("script");
	r.setAttribute("src", "https://www.googletagmanager.com/gtag/js?id=G-3HQGV5BC38"), r.setAttribute("type", "text/javascript"), r.setAttribute("crossOrigin", "anonymous"),  r.onload = function (){
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
      
        gtag('config', 'G-3HQGV5BC38');
        var ads = document.createElement('script');
        ads.setAttribute("src", "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7889675448259925"), ads.setAttribute("type", "text/javascript"), ads.setAttribute("crossOrigin", "anonymous"), ads.onload = function(){
            (adsbygoogle = window.adsbygoogle || []).push({});
            (adsbygoogle = window.adsbygoogle || []).push({});
            (adsbygoogle = window.adsbygoogle || []).push({});
            (adsbygoogle = window.adsbygoogle || []).push({});
        },document.head.appendChild(ads);
    },document.head.appendChild(r);
}
window.addEventListener('load', function() {
    loadGA();
});