'use strict';

console.log('yey')

const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const canvas2 = document.getElementById('canvas2');
const canvas3 = document.getElementById('canvas3');
const canvas4 = document.getElementById('canvas4');
const canvas5 = document.getElementById('canvas5');
const snap = document.getElementById("snap");
const delete1 = document.getElementById('button-delete-1')
const delete2 = document.getElementById('button-delete-2')
const delete3 = document.getElementById('button-delete-3')
const delete4 = document.getElementById('button-delete-4')
const delete5 = document.getElementById('button-delete-5')
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
            canvas.style.display = "inherit"
            var context = canvas.getContext('2d');
            context.drawImage(video, 0, 0, 1280, 720);
            snap.value = "2"
            image_count.splice(0, 0, 1)
        }
        else if(snap.value == "2"){
            canvas2.style.display = "inherit"
            var context = canvas2.getContext('2d');
            context.drawImage(video, 0, 0, 1280, 720);
            snap.value = "3"
            image_count.splice(0, 0, 1)
        }
        else if(snap.value == "3"){
            canvas3.style.display = "inherit"
            var context = canvas3.getContext('2d');
            context.drawImage(video, 0, 0, 1280, 720);
            snap.value = "4"
            image_count.splice(0, 0, 1)
        }
        else if(snap.value == "4"){
            canvas4.style.display = "inherit"
            var context = canvas4.getContext('2d');
            context.drawImage(video, 0, 0, 1280, 720);
            snap.value = "5"
            image_count.splice(0, 0, 1)
        }
        else{
            canvas5.style.display = "inherit"
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



delete1.addEventListener("click", function() {
    event.preventDefault()
    canvas.style.display = "none"
    const context1 = canvas.getContext('2d');
    context1.clearRect(0, 0, canvas.width, canvas.height);
    snap.value = 1

    if(document.getElementById('imageDataURL2')){
        console.log('masuk 2');
        canvas.style.display = "inherit"
        context1.drawImage(canvas2, 0, 0)
        const context2 = canvas2.getContext('2d');
        context2.clearRect(0, 0, canvas2.width, canvas2.height);
        document.getElementById('imageDataURL1').setAttribute('value', canvas.toDataURL("image/jpeg", 0.5))
        canvas2.style.display = "none"
        snap.value = 2

        if(document.getElementById('imageDataURL3')){
            console.log('masuk 3');
            canvas2.style.display = "inherit"
            context2.drawImage(canvas3, 0, 0)
            const context3 = canvas3.getContext('2d');
            context3.clearRect(0, 0, canvas3.width, canvas3.height);
            // document.getElementById('imageDataURL3').remove()
            document.getElementById('imageDataURL2').setAttribute('value', canvas2.toDataURL("image/jpeg", 0.5))
            canvas3.style.display = "none"
            snap.value = 3

            if(document.getElementById('imageDataURL4')){
                console.log('masuk 4');
                canvas3.style.display = "inherit"
                context3.drawImage(canvas4, 0, 0)
                const context4 = canvas4.getContext('2d');
                context4.clearRect(0, 0, canvas4.width, canvas4.height);
                // document.getElementById('imageDataURL3').remove()
                document.getElementById('imageDataURL3').setAttribute('value', canvas3.toDataURL("image/jpeg", 0.5))
                canvas4.style.display = "none"
                snap.value = 4
                
                if(document.getElementById('imageDataURL5')){
                    console.log('masuk 5');
                    canvas4.style.display = "inherit"
                    context4.drawImage(canvas5, 0, 0)
                    const context5 = canvas5.getContext('2d');
                    context5.clearRect(0, 0, canvas5.width, canvas5.height);
                    // document.getElementById('imageDataURL3').remove()
                    document.getElementById('imageDataURL4').setAttribute('value', canvas4.toDataURL("image/jpeg", 0.5))
                    canvas5.style.display = "none"
                    snap.value = 5
                    document.getElementById('imageDataURL5').remove()
                }
                else{
                    console.log('else5');
                    document.getElementById('imageDataURL4').remove()
                }
                
            }
            else{
                console.log('else4')
                document.getElementById('imageDataURL3').remove()
            }
        }
        else{
            console.log('else3')
            document.getElementById('imageDataURL2').remove()
        }
    }
    else{
        console.log('else2')
        document.getElementById('imageDataURL1').remove()
    }
})


delete2.addEventListener("click", function() {
    event.preventDefault()
    canvas2.style.display = "none"
    const context2 = canvas2.getContext('2d');
    context2.clearRect(0, 0, canvas2.width, canvas2.height);
    snap.value = 2

    if(document.getElementById('imageDataURL3')){
        console.log('masuk 2-3');
        canvas2.style.display = "inherit"
        context2.drawImage(canvas3, 0, 0)
        const context3 = canvas3.getContext('2d');
        context3.clearRect(0, 0, canvas3.width, canvas3.height);
        // document.getElementById('imageDataURL3').remove()
        document.getElementById('imageDataURL2').setAttribute('value', canvas2.toDataURL("image/jpeg", 0.5))
        canvas3.style.display = "none"
        snap.value = 3

        if(document.getElementById('imageDataURL4')){
            console.log('masuk 4');
            canvas3.style.display = "inherit"
            context3.drawImage(canvas4, 0, 0)
            const context4 = canvas4.getContext('2d');
            context4.clearRect(0, 0, canvas4.width, canvas4.height);
            // document.getElementById('imageDataURL3').remove()
            document.getElementById('imageDataURL3').setAttribute('value', canvas3.toDataURL("image/jpeg", 0.5))
            canvas4.style.display = "none"
            snap.value = 4

            if(document.getElementById('imageDataURL5')){
                console.log('masuk 5');
                canvas4.style.display = "inherit"
                context4.drawImage(canvas5, 0, 0)
                const context5 = canvas5.getContext('2d');
                context5.clearRect(0, 0, canvas5.width, canvas5.height);
                // document.getElementById('imageDataURL3').remove()
                document.getElementById('imageDataURL4').setAttribute('value', canvas4.toDataURL("image/jpeg", 0.5))
                canvas5.style.display = "none"
                snap.value = 5
                document.getElementById('imageDataURL5').remove()
            }
            else{
                console.log('else5')
                document.getElementById('imageDataURL4').remove()
            }
        }
        else{
            console.log('else4')
            document.getElementById('imageDataURL3').remove()
        }
    }
    else{
        console.log('else3')
        document.getElementById('imageDataURL2').remove()
    }
})

delete3.addEventListener("click", function() {
    event.preventDefault()
    canvas3.style.display = "none"
    const context3 = canvas3.getContext('2d');
    context3.clearRect(0, 0, canvas3.width, canvas3.height);
    snap.value = 3

    if(document.getElementById('imageDataURL4')){
        console.log('masuk 4');
        canvas3.style.display = "inherit"
        context3.drawImage(canvas4, 0, 0)
        const context4 = canvas4.getContext('2d');
        context4.clearRect(0, 0, canvas4.width, canvas4.height);
        // document.getElementById('imageDataURL3').remove()
        document.getElementById('imageDataURL3').setAttribute('value', canvas3.toDataURL("image/jpeg", 0.5))
        canvas4.style.display = "none"
        snap.value = 4

        if(document.getElementById('imageDataURL5')){
            console.log('masuk 5');
            canvas4.style.display = "inherit"
            context4.drawImage(canvas5, 0, 0)
            const context5 = canvas5.getContext('2d');
            context5.clearRect(0, 0, canvas5.width, canvas5.height);
            // document.getElementById('imageDataURL3').remove()
            document.getElementById('imageDataURL4').setAttribute('value', canvas4.toDataURL("image/jpeg", 0.5))
            canvas5.style.display = "none"
            snap.value = 5
            document.getElementById('imageDataURL5').remove()
        }
        else{
            console.log('else5')
            document.getElementById('imageDataURL4').remove()
        }
    }
    else{
        console.log('else4')
        document.getElementById('imageDataURL3').remove()
    }
})

delete4.addEventListener("click", function() {
    event.preventDefault()
    canvas4.style.display = "none"
    const context4 = canvas4.getContext('2d');
    context4.clearRect(0, 0, canvas4.width, canvas4.height);
    snap.value = 4

    if(document.getElementById('imageDataURL5')){
        console.log('masuk 5');
        canvas4.style.display = "inherit"
        context4.drawImage(canvas5, 0, 0)
        const context5 = canvas5.getContext('2d');
        context5.clearRect(0, 0, canvas5.width, canvas5.height);
        // document.getElementById('imageDataURL3').remove()
        document.getElementById('imageDataURL4').setAttribute('value', canvas4.toDataURL("image/jpeg", 0.5))
        canvas5.style.display = "none"
        snap.value = 5
        document.getElementById('imageDataURL5').remove()

    }
    else{
        console.log('else5')
        document.getElementById('imageDataURL4').remove()
    }
})

delete5.addEventListener("click", function() {
    event.preventDefault()
    canvas5.style.display = "none"
    const context5 = canvas5.getContext('2d');
    context5.clearRect(0, 0, canvas5.width, canvas5.height);
    snap.value = 5
    document.getElementById('imageDataURL5').remove()

})
