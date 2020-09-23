'use strict';

console.log('yey')

const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const canvas2 = document.getElementById('canvas2');
const canvas3 = document.getElementById('canvas3');
const canvas4 = document.getElementById('canvas4');
const canvas5 = document.getElementById('canvas5');
const snap = document.getElementById("snap");
const errorMsgElement = document.getElementById('span#errorMsg');
let image_count = [0, 0, 0, 0, 0]


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
        window.stream = stream;
        video.srcObject = stream;
        video.play();
    }

    // Load init
    init();

    // Draw image
    
    snap.addEventListener("click", function() {
        event.preventDefault();
        if(snap.value == "1"){
            var context = canvas.getContext('2d');

            context.drawImage(video, 0, 0, 1280, 720);
            snap.value = "2"
            image_count.splice(0, 0, 1)
        }
        else if(snap.value == "2"){
            var context = canvas2.getContext('2d');

            context.drawImage(video, 0, 0, 1280, 720);
            snap.value = "3"
            image_count.splice(0, 0, 1)
        }
        else if(snap.value == "3"){
            var context = canvas3.getContext('2d');

            context.drawImage(video, 0, 0, 1280, 720);
            snap.value = "4"
            image_count.splice(0, 0, 1)
        }
        else if(snap.value == "4"){
            var context = canvas4.getContext('2d');

            context.drawImage(video, 0, 0, 1280, 720);
            snap.value = "5"
            image_count.splice(0, 0, 1)
        }
        else{
            var context = canvas5.getContext('2d');

            context.drawImage(video, 0, 0, 1280, 720);
            snap.value = "1"
            image_count.splice(0, 0, 1)
        }

        let count_image = 0
        for (let index = 0; index < image_count.length; index++) {
            if (image_count[index] == 1){
                count_image++
            }
        }

        // for (let index = 0; index < image_count.length; index++) {
        //     const image64URL = document.createElement('input')
            // let image64;
            // if (index == 0) {
            //     image64 = canvas.toDataURL("image/jpeg", 0.5)
            // }
            // else if(index == 1){
            //     image64 = canvas2.toDataURL("image/jpeg", 0.5)
            // }
            // else if(index == 2){
            //     image64 = canvas3.toDataURL("image/jpeg", 0.5)
            // }
            // else if(index == 3){
            //     image64 = canvas4.toDataURL("image/jpeg", 0.5)
            // }
            // else if(index == 4){
            //     image64 = canvas5.toDataURL("image/jpeg", 0.5)
            // }
            
        //     if (image_count[index] == 1 ){
        //         let new_index = index + 1
        //         if(document.getElementById('imageDataURL'+ new_index.toString())){
        //             console.log('sudah ada')
        //             const image64URL = document.getElementById('imageDataURL'+ new_index.toString())
        //             image64URL.setAttribute('value', image64)
                    
        //         }
        //         else{
        //             console.log('buat baru')
        //             const image64URL = document.createElement('input')
        //             image64URL.setAttribute('type', 'text')
        //             image64URL.setAttribute('name', 'imageDataURL'+new_index.toString())
        //             image64URL.setAttribute('value', image64)
        //             image64URL.setAttribute('id', 'imageDataURL'+new_index.toString())
        //             image64URL.hidden = "true"
        //             document.getElementById("formDiv").appendChild(image64URL)
        //         }
        //     }
        // }
        let current
        if(snap.value == "1"){
            current = 5
        }
        else{
            current = parseInt(snap.value) - 1
        }
        alert(current)

        let image64;
        if (current == 1) {
            image64 = canvas.toDataURL("image/jpeg", 0.5)
        }
        else if(current == 2){
            image64 = canvas2.toDataURL("image/jpeg", 0.5)
        }
        else if(current == 3){
            image64 = canvas3.toDataURL("image/jpeg", 0.5)
        }
        else if(current == 4){
            image64 = canvas4.toDataURL("image/jpeg", 0.5)
        }
        else if(current == 5){
            image64 = canvas5.toDataURL("image/jpeg", 0.5)
        }

        if(document.getElementById('imageDataURL'+ current.toString())){
            document.getElementById('imageDataURL'+ current.toString()).setAttribute('value', image64)
        }
        else{
            const image64URL = document.createElement('input')

            image64URL.setAttribute('type', 'text')
            image64URL.setAttribute('name', 'imageDataURL' + current.toString())
            image64URL.setAttribute('value', image64)
            image64URL.setAttribute('id', 'imageDataURL' + current.toString())
            image64URL.hidden = "true"
            document.getElementById("formDiv").appendChild(image64URL)
        }
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