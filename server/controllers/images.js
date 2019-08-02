var mongoose = require('mongoose');
var conn = mongoose.connection;
let articles = require('../controllers/articles');
var https = require('https');
var fs = require('fs');
const Grid = require('gridfs-stream');
var mongodb = require('mongodb');

let gfs,bucket;

conn.once('open', () => {
    // Init stream
    gfs = Grid(conn.db, mongoose.mongo);
    bucket = new mongodb.GridFSBucket(conn.db);
});

var download = function(url, dest, cb) {
    console.log("Downloading");
    var file = fs.createWriteStream(dest);

    file.on('open',function (fd){
        console.log("created file "+fd)
        https.get(url, function(response) {
            response.pipe(file);
            file.on('finish', function() {
                file.close();
                cb(file);
            });
        });
    });
};

function downloadAndSaveImage(image,callback) {
    console.log("Init download");
    article = articles.getArticlesById(image, function (article) {
        download(article['imageUrl'],'/home/rsa-key-20190326/snap/server/res/image/'+image+'.jpg',function (file) {
            console.log("Downloaded");
            fs.createReadStream(file.path)
                .pipe(bucket.openUploadStream(image))
                .on('error',function (err) {
                    console.log(err);
                    callback(file.path);
                })
                .on('finish',function () {
                    console.log("finished");
                    callback(file.path);
                });
        });
    });
}

//4.7.3
exports.getImage = function(req, res) {
    console.log("Got request");
    gfs.files.findOne({filename: req.params.image}, function(err, file){

        if(!file || file.length === 0){
            console.log("Doesnt exist");

            downloadAndSaveImage(req.params.image, function (file) {
                console.log("Saved");
                var readstream = fs.createReadStream(file);
                // set the proper content type
                res.set('Content-Type', 'image/jpg');
                // Return response
                console.log("Returned");
                return readstream.pipe(res);
            });
        }else{
            console.log("Exist");
            var readstream = gfs.createReadStream({
                filename: file.filename,
            });
            readstream.on('error', function (err) {
                console.log('An error occurred!', err);
                throw err;
            });

            return readstream.pipe(res);
        }
    });
};

exports.getImageCount = function (callback) {
    gfs.files.count(function (err, count) {
        if (err)
            callback(0);
        callback(count);
    });
};