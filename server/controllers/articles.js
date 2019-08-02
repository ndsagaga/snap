var Article = require('mongoose').model('Article'),
    images = require('../controllers/images');

exports.getArticles = function (req, res) {
    Article.find({}).exec(function (err, collection) {
        if (err)
            console.log(err);
        res.send(collection);
    })
};

exports.getArticlesById = function (id, cb) {
    Article.findOne({id: {$eq: id}}, function (err, collection) {
        if (err) {
            console.log("ERROR 1");
            cb(null);
        }
        console.log("17: " + collection);
        cb(collection);
    })
};

exports.addCommentToArticle = function (req, res) {
    if (!req.body.hasOwnProperty('comment')) {
        res.send();
        return;
    }

    Article.findOneAndUpdate({id: {$eq: req.params.id}}, {
        $push: {
            comments: {
                content: req.body.comment,
                timestamp: (new Date()).getTime()
            }
        }
    }, function (err, success) {
        if (err) {
            console.log("ERR");
            res.status(404).send();
        } else {
            console.log(success)
            res.send(success)
        }
    })
};

var getArticlesForQuery = exports.getArticlesForQuery = function (req, res) {
    var t = Date.now();
    Article.find({$text: {$search: req.body.searchbox}}).exec(function (err, collection) {
        t = Date.now() - t;
        var result = {result:"success",ip:getIP(req),loc:{lat:req.body.lat,long:req.body.long},time:t,data:collection,images:images.getImageCount};
        res.send(collection);
    })
};

exports.getArticlesForQueryWithLocation = function (req, res) {
    if (!req.body.hasOwnProperty('lat') || !req.body.hasOwnProperty('long')) {
        console.log("WARNING: NO COORDINATES. PASSING ON TO REGULAR HANDLER!");
        getArticlesForQuery(req, res);
        return;
    }

    if (req.body.searchbox.length == 0) {
        res.send([]);
        return;
    }

    console.log(req.body.lat, req.body.long)
    var t = Date.now();
    Article.find({
        $or: [
            {content: {$regex: req.body.searchbox, $options: 'i'}},
            {
                title: {$regex: req.body.searchbox, $options: 'i'}
        }]
    }).near('location', {center: [req.body.long, req.body.lat], spherical: true}).exec(function (err, collection) {
        if (err) throw err;
        images.getImageCount(function (count) {
            t = Date.now() - t;
            var result = {result:"success",ip:getIP(req),loc:{lat:req.body.lat,long:req.body.long},time:t,images:count,data:collection};
            res.send(result);
        });
    })
};

function getIP(req) {
    var ip = req.connection.remoteAddress ||
        req.socket.remoteAddress ||
        (req.connection.socket ? req.connection.socket.remoteAddress : null);

    if (ip === null)
        return ip;

    return ip.substring(6);
}