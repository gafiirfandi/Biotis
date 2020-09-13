'use strict';

console.log('yey')

const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const snap = document.getElementById("snap");
const errorMsgElement = document.getElementById('span#errorMsg');

// check whether we can use facingMode
let faceMode = document.getElementById("input_cam")
let supports = navigator.mediaDevices.getSupportedConstraints();
if( supports['facingMode'] === true ) {
  faceMode.disabled = false;
}
// console.log(faceMode.value)

let constraints = {
    video: {
        width: 1280, height: 720, facingMode: faceMode.value
    }
};


function capture(){
    // Access webcam
    async function init() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            handleSuccess(stream);
        } catch (e) {
            errorMsgElement.innerHTML = `navigator.getUserMedia error:${e.toString()}`;
        }
    }

    // Success
    function handleSuccess(stream) {
        console.log(constraints)
        window.stream = stream;
        video.srcObject = stream;
        video.play();
    }

    // Load init
    init();

    // Draw image
    var context = canvas.getContext('2d');
    snap.addEventListener("click", function() {
        event.preventDefault();
        context.drawImage(video, 0, 0);
        // console.log(video)
        // console.log(video.srcObject)
        // console.log(canvas.toDataURL("image/jpg", 0))
        const image64URL = document.createElement('input')
        const image64 = canvas.toDataURL("image/jpeg", 0.5)
        console.log(image64)
        image64URL.setAttribute('type', 'text')
        image64URL.setAttribute('name', 'imageDataURL')
        image64URL.setAttribute('value', image64)
        image64URL.hidden = "true"
        document.getElementById("formDiv").appendChild(image64URL)


        var a = document.createElement('a')
        a.href = image64

        // canvas.toBlob(function(blob) {
        //     var newImg = document.createElement('img'), url = URL.createObjectURL(blob);
          
        //     newImg.onload = function() {
        //       // no longer need to read the blob so it's revoked
        //       URL.revokeObjectURL(url);
        //     };
          
        //     newImg.src = url;
        //     document.body.appendChild(newImg);
        //   });

        a.download = "gafi.jpg"
        // a.click()
    });
}

faceMode.addEventListener("change", function() {
    video.srcObject.getTracks().forEach(t => {
        t.stop();
      });
    video.srcObject = null
    constraints = {
        video: {
            width: 1280, height: 720, facingMode: faceMode.value
        }
    };
    // console.log(constraints)
    
    capture()
    
});

capture()