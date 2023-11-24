
var chatStart = 0; // 채팅 시작 상태 플래그
var isApiCalling = false; // API 호출 상태 플래그
var promptId; // 현재 프롬프트의 ID
var recognition; // 음성 인식 객체
var recognitionActive = false
var chatPlayPause = new Audio(); 
    chatPlayPause.preload = 'auto'; // 오디오 파일 미리 로드
    chatPlayPause.src = 'audio//start.mp3'    
var audioPlayer = new Audio(); // 오디오 플레이어 객체
audioPlayer.preload = 'auto'; // 오디오 파일 미리 로드
// audioPlayer.src = 'audio\\hello-GTalk.mp3'; // 오디오 파일 경로 설정
audioPlayer.src = 'audio//start.mp3'

var userIcon = '<i class="fa-solid fa-user text-secondary"></i> '; // 사용자 아이콘 HTML
var aiIcon = '<img  class="aiIcon" src="images/gtalk-white.png" width="20"> '; // AI 아이콘 HTML
var micIcon=`
        <div class="ps-3 micIcon chat-play-pause-button cursor-pointer ">
            <i class="standby-Mic fa-duotone fa-microphone fs-1"></i>
       </div>`
var stopWords  = ['종료', '그만', '바이','마이크'];   
var startWords = ['다시', '안녕', '지톡','톡톡'];       
clientDevicesId=""

$(document).ready(function() {
    binding()

    var selectedTheme = localStorage.getItem('theme') ? localStorage.getItem('theme') : 'light'; // 저장된 테마를 가져옵니다.
    clientDevicesId= localStorage.getItem('clientDevicesId') ?  localStorage.getItem('clientDevicesId'): randomKey(16);
    localStorage.setItem('clientDevicesId', clientDevicesId); 
    $("#clientDevicesId").text( clientDevicesId)
    
    $('#bg-theme').val(selectedTheme);

    bg_change( selectedTheme )

    
    $('.bg-theme').click(function() {
        var selectedTheme = $(this).attr("bg-theme"); // 선택된 테마 값을 가져옵니다.
        localStorage.setItem('theme', selectedTheme); // 선택된 테마를 localStorage에 저장합니다.
        bg_change( selectedTheme );
        $(this).blur();
        
    });
    $("#clientDevicesId").click( function(){
        $("#clientDevicesId").addClass("d-none")
    })
    // 윈도우 크기가 변경될 때마다 높이를 업데이트합니다.
   $(window).resize(updateChatHeight);
   // 초기 로딩 시에도 #chat 요소의 높이를 설정합니다.
   updateChatHeight();
})
function binding(){
    $("#start-chat-button").unbind()
    $("#chat-play-pause").unbind()
    $("#chat-play-pause-button").unbind()
    $(".chat-play-pause-button").unbind()
    $("#start-chat-button").click(function() {
        isApiCalling = false; // API 호출 상태를 false로 초기화
        initializeRecognition(); // 음성 인식 초기화
        $(".start-info").hide(500,function(){
            $("#chat-play-pause-button").show(500)
            $(".micIcon").show(500)
            $("#chat-play-pause-container").show(300);
            $("#youtube-video-container").show(500);
            chatStart = 1; // 채팅 시작 플래그를 true로 설정
            audioPlayer.play(); // 오디오 재생
            chatPlayPause.play();
        })
        $(".fs-1").hide();
        $(".container").addClass("no-margin-padding");
        $(".chat-box-container").addClass("chat-box-moved"); // chat-box-container에 새로운 클래스 추가
        $(".youtube-video-container").addClass("youtube-embed");
    });
    $(".chat-play-pause-button").click(function(event) {
        event.stopPropagation();
        if ($('.standby-Mic').hasClass('text-secondary')) {
            chat_start()
        } else {
            chat_stop()
        } 

    });
    $("#chat-play-pause").click(function(event) {
        event.stopPropagation();
        if ($(this).attr("state-Chat")=='pause' ) {
            chat_start(this)
        } else {
            chat_stop(this)
        } 

    });
}    
function chat_start(_this){
    isApiCalling = false; // API 호출 상태를 false로 초기화
    initializeRecognition(); // 음성 인식 초기화
    $(".standby-Mic").remove()
    chatStart = 1; // 채팅 시작 플래그를 true로 설정
    //audioPlayer.play(); // 오디오 재생
    chatPlayPause.play();
    $("#chat-play-pause").attr("state-Chat",'chatStart')
    $(".start-info").hide(500)
    $("#chat-box").append(`${micIcon}`);  binding();
    $("#chat-play-pause-button").show(500)
    $(".micIcon").show(500)
    recognition.start(); // 음성 인
   
};
function chat_stop(){
    
    chatStart =0; // 채팅 시작 플래그
    isApiCalling = false; // API 호출 상태를 false로 초기화
    $(".standby-Mic").remove() 
    chatPlayPause.play();
    $("#chat-box").append(`${micIcon}`);  binding();
    $(".standby-Mic").addClass("text-secondary")
    $("#chat-play-pause").attr("state-Chat",'pause')
    recognition.stop(); // 음성 인식 종료
    
};
function downLoad(fileName) {    
    window.location.href = '/download/' + fileName; // 파일 이름을 URL에 추가하여 서버에 요청
}
// 오디오 재생 완료 이벤트 핸들러 설정
audioPlayer.onended = function() {
    if( chatStart==0 ) { 
        $("#chat-box").append(`${micIcon}`);
        $(".standby-Mic").addClass("text-secondary")
        
        $("#chat-play-pause").attr("state-Chat",'pause')
        binding();
        return  } 
    isApiCalling = false; // 오디오 재생 완료 후 API 호출 상태를 false로 변경
    if (chatStart) { // 사용자가 채팅을 시작한 상태라면
        recognition.start(); // 음성 인식을 재시작
    }
    $("#chat-play-pause").attr("state-Chat",'chatStart')
    $("#chat-box").append(`${micIcon}`);  binding();
    $('html, body').animate({
        scrollTop: $(document).height()
    }, 1000);
};

function initializeRecognition() {
    window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.interimResults = true;
    recognition.lang = 'ko-KR';
    recognition.onstart = function() {
        console.log("음성 인식 시작됨");
        promptId = "prompt-" + Math.random().toString(36).substring(2, 12);
    };
    recognition.onend = function() {
        if( chatStart==0 ) { return  } 
        recognitionActive = false
        console.log("음성 인식 종료됨");
        
        if ( ! isApiCalling ) { // API 호출 중이 아니면
            send_prompt(promptId); // send_prompt 함수 호출
        }
    };
    recognition.onerror = function(event) {
        if( chatStart==0 ) { return  } 
        recognitionActive = false
        console.log("음성 인식 오류 발생: " + event);
        
        if ( ! isApiCalling ) { 
            try {
                recognition.start()       
            } catch (error) {
                
            }
            
        }
        
    };
    recognition.onresult = function(event) {
        if( chatStart==0 ) { return  } 
        recognitionActive = true;
        var texts = Array.from(event.results).map(result => result[0].transcript).join("");
        if ($('#' + promptId).length == 0) {
            $('#chat').append($('<p>').attr('id', promptId));
        }
        
        $('#' + promptId).html(userIcon + texts);
    };
}


function send_prompt(currentPromptId) {
    var promptText = $('#' + currentPromptId).text().trim();
    if (promptText === "") {
        try { recognition.start()} catch (error) {}
       
        return; // 프롬프트가 비어 있으면 여기서 함수 종료
    }
    // var shouldStop = stopWords.some(function(stopWord) { // Using Array.prototype.some for brevity.
    //     return promptText.includes(stopWord);
    // });

    // if (shouldStop) { 
    //     chat_stop();
    //     return
    // }

    isApiCalling = true; // API 호출 상태를 true로 설정
    recognition.stop(); // 음성 인식 중지
    var aiChatId = "ai-" + Math.random().toString(36).substring(2, 10);
    $(".micIcon").hide(500,function(){ $(this).remove()})
    // $("#chat-box").append(`<p id="${aiChatId}"><span id="loading" class="loading"></span></p>`);
    startLoadingAnimation();
    // alert( clientDevicesId )
    $.ajax({
        url: "/query",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({query: promptText}),
        success: function(response) {
            
            stopLoadingAnimation()
            $("#chat").scrollTop($("#chat")[0].scrollHeight);
            // $('html, body').scrollTop($(document).height());
            // audioPlayer.src = 'chat_audio/' + aiChatId + '.mp3'
            // audioPlayer.play().then( function(){
            //     stopLoadingAnimation(); // 
                
            //     $('html, body').animate({
            //         scrollTop: $(document).height()
            //     }, 3000);
            // // var shouldStop = stopWords.some(function(word) {return  promptText.includes(word) ||  response.answer.includes(word);});
            // //     if (shouldStop) {  $(".standby-Mic").remove();chat_stop()}
            // }); 
            
        },
        error: function(err) {
            stopLoadingAnimation(); // 
            console.log("Error occurred:", err);
            $('#' + aiChatId).html("Server Error!");
            // audioPlayer.src = 'audio//start.mp3'
            // audioPlayer.play().then( function(){
            //     $('html, body').scrollTop($(document).height());
            // })
        }
        
    });
    $("#chat").scrollTop($("#chat")[0].scrollHeight);
   
}


function bg_change( selectedTheme ){
    var changColor=['bg-warning','bg-white','text-danger']
    if ( selectedTheme =="dark"){
           $(".aiIcon").attr("src","images/gtalk-white.png")
            $.each( changColor, function(index, colorClass){
                $(`.${colorClass}`).addClass(`${colorClass}-remove`).removeClass(`${colorClass}`);
            })

    } else {
          $(".aiIcon").attr("src","images/GTalk-trans-40.png")
            $.each( changColor, function(index, colorClass){
                $(`.${colorClass}-remove`).addClass(`${colorClass}`).removeClass(`${colorClass}-remove`);   
            })
   }
   $('html').attr('data-bs-theme', selectedTheme); 

}
var loadingAnimation; // Declare the variable to store interval ID globally
function startLoadingAnimation() {
    loadingAnimation = setInterval(function() {
        $('#loading').text(function(index, text) {
            return text.length < 30 ? text + '.' : '.';
        });
    }, 1000); // Start an interval to add a dot every 1000 milliseconds
}

function stopLoadingAnimation() {
    clearInterval(loadingAnimation); // Clear the interval
    $('#loading').text(''); // Clear the loading text
}
function randomKey(n){
   var randomStr=Math.random().toString(36).substring(2, 10) + Math.random().toString(36).substring(2, 10)
    return randomStr.substring(0, n-1);
}
function handleEnter(event) {

    if (event.which === 13 && !event.shiftKey) { // Shift가 아닌 Enter만 눌렸을 때
        event.preventDefault(); // 엔터 키의 기본 동작(새 줄 추가)을 막습니다.
        send_query(); // 메시지 전송 함수 호출
    } else if (event.which === 13 && event.shiftKey) {
        var textarea = $('#query').val();
        var lines = textarea.split("\n").length;
            lines = lines <10 ? lines : 9 
           $('#query').attr('rows', lines + 1); // 한 줄 추가
    }
}
document.addEventListener('DOMContentLoaded', function () {
    // 'start-chat-button' 클릭 이벤트 리스너 추가
    document.getElementById('start-chat-button').addEventListener('click', function () {
        // 'main-page'를 보이게 설정
        document.getElementById('main-page').style.display = 'block';
        // 이 버튼을 숨기는 추가적인 코드 (선택 사항)
        this.style.display = 'none';
    });
});

$('#navbarToggleBtn').click(function() {  $('#navbarNav').toggleClass('show'); });

function send_query() {

        var query = $("#query").val();
        if (query.trim() === "") return;

        var chatId=Math.random().toString(36).substring(2, 10)
        var htmlQuery = marked.parse(query);
        // $("#chat").append(`
        
        //         <div class='user_query  d-flex p-2  text-secondary'>
        //                 <div ><i class="fa-thin fa-user fs-4"></i></div>
        //                 <div id="user-${chatId}" class="ms-2" >${htmlQuery}</div>
        //         </div>
        // `);


        
        if ($('#' + chatId).length == 0) {
            $('#chat').append($('<p>').attr('id', chatId));
        }
        
        $('#' + chatId).html(userIcon + query);
    
        
        $("#query").val("Waiting ... !");
        $('#query').attr('rows', 1);
        $("#query").prop('disabled', true);

    
          $.ajax({
            url: "/query",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ query: query }),
            success: function (response) {
            
                $("#query").val("");
                $("#chat").scrollTop($("#chat")[0].scrollHeight);         
                $("#query").prop('disabled', false);
                // 스크롤 위치를 가장 하단으로 이동
               
            },
            error: function () {
                $("#query").val("");
                $("#query").prop('disabled', false);
                $("#chat").scrollTop($("#chat")[0].scrollHeight);
            }
        });

        // 사용자가 메시지를 보낼 때도 스크롤 위치를 조정
        $("#chat").scrollTop($("#chat")[0].scrollHeight);
}
