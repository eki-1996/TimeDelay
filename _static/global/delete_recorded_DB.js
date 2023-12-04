let stopButton = document.getElementById('stopButton');
let download_link = document.querySelector("#download-video");
let mediaRecorder = null;
let mediaStream = null;
let recordedChunks = [];
let blobdata = null;
let put;
let imgFile;
let db;
let dbName = 'webcamDB';

window.onload = async () => {

    mediaStream = await navigator.mediaDevices.getUserMedia({ 
        video: {
        width: 1920,
        height: 1080
    }, audio: false });

    mediaRecorder = new MediaRecorder(mediaStream, { mimeType: 'video/webm' });

    mediaRecorder.addEventListener('dataavailable', function(event) {
        // console.log(
        //     event.type, // The type of the event
        //     event.target, // The target of the event
        //     event, // The event itself
        //     (() => {try {throw new Error();} catch(e) {return e;}})() // A stacktrace to figure out what triggered the event
        //   );
		recordedChunks.push(event.data);
    });

    // event : recording stopped & all blobs sent
    mediaRecorder.addEventListener('stop', function(event) {
        console.log(
            event.type, // The type of the event
            event.target, // The target of the event
            event, // The event itself
            (() => {try {throw new Error();} catch(e) {return e;}})() // A stacktrace to figure out what triggered the event
          );
    	// create local object URL from the recorded video blobs
    	// let video_local = URL.createObjectURL(new Blob(blobs_recorded, { type: 'video/webm' }));
        // blobdata = URL.createObjectURL(new Blob(recordedChunks, { type: 'video/webm' }));
        blobdata = new Blob(recordedChunks, { type: 'video/webm' });
        console.log(blobdata)

        // store video blob data to indexedDB
        // var dbName = 'webcamDB';
        var storeName  = 'webcamStore';

        // var deleteReq = indexedDB.deleteDatabase(dbName);

        // deleteReq.onsuccess = function(event){
        //     console.log('db delete success');
        //     // 存在しないDB名を指定してもこっちが実行される
        // }

        // deleteReq.onerror = function(){
        //     console.log('db delete error');
        // }

        var openReq  = indexedDB.open(dbName);
        //　DB名を指定して接続。DBがなければ新規作成される。

        openReq.onupgradeneeded = function(event){
        //onupgradeneededは、DBのバージョン更新(DBの新規作成も含む)時のみ実行
            console.log('db upgrade');
            db = event.target.result;
            // db.createObjectStore(storeName, {keyPath: 'id', autoIncrement: true})
            db.createObjectStore(storeName)
        }
        openReq.onsuccess = function(event){
        //onupgradeneededの後に実行。更新がない場合はこれだけ実行
            console.log('db open success');
            db = event.target.result;
            var transaction = db.transaction(storeName, 'readwrite');
            transaction.oncomplete = function(){
                console.log("Success transaction");
            };
            // put video blobdata into indexedDB
            put = transaction.objectStore(storeName).put(blobdata, "video" + String(js_vars.cnt))
            console.log(put)
            let videolist = []
            for(var item of js_vars.list) {
                var transaction_infor = db.transaction(storeName, 'readwrite');
                // get video blobdata from indexedDB
                transaction_infor.objectStore(storeName).get("video" + String(item)).onsuccess = function (event) {
                    console.log(item)
                    imgFile = event.target.result;
                    console.log("Got video!" + imgFile);
                    console.log(imgFile)
                    videolist.push(imgFile)
                    // after get all video blob data, create a new url to a download link.
                    if (item == js_vars.cnt) {
                        console.log("videolist")
                        console.log(videolist)
                        var imgURL = URL.createObjectURL(new Blob(videolist, { type: 'video/webm' }));
                        download_link.href = imgURL;
                    }
                };
                transaction_infor.oncomplete = function(){
                    console.log("Success read transaction");
                };
                transaction_infor.onerror = function(){
                    console.log("failed read transaction");
                };
            }
            
        }
        openReq.onerror = function(event){
        // 接続に失敗
            console.log('db open error');
        }
    });

    mediaRecorder.start(1000);
};

// window.onbeforeunload = () => {
//     mediaRecorder.stop();
//     console.log("end")
// };
window.onbeforeunload = () => {
    db.close();
    var deleteReq = indexedDB.deleteDatabase(dbName);

    deleteReq.onsuccess = function(event){
        console.log('db delete success');
        // 存在しないDB名を指定してもこっちが実行される
    }

    deleteReq.onerror = function(){
        console.log('db delete error');
    }
    console.log("end");
};

stopButton.addEventListener('click', () => {
    mediaRecorder.stop();
});

// function blobToArrayBuffer(blob) {
//     return new Promise((resolve, reject) => {
//       const reader = new FileReader();
//       reader.addEventListener('loadend', () => {
//         resolve(reader.result);
//       });
//       reader.addEventListener('error', reject);
//       reader.readAsArrayBuffer(blob);
//     });
//   }
  