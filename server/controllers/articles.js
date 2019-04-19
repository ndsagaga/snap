var Article = require('mongoose').model('Article');

exports.getArticles = function (req, res) {
    Article.find({}).exec(function (err, collection) {
        if (err)
            console.log(err);
        res.send(collection);
    })
};

var getArticlesForQuery = exports.getArticlesForQuery = function (req, res) {
    Article.find({$text: {$search: req.body.searchbox}}).exec(function (err, collection) {
        res.send(collection);
    })
};

exports.getArticlesForQueryWithLocation = function (req, res) {
    if (!req.body.hasOwnProperty('lat') || !req.body.hasOwnProperty('long')) {
        console.log("WARNING: NO COORDINATES. PASSING ON TO REGULAR HANDLER!");
        getArticlesForQuery(req, res);
        return;
    }

    console.log(req.body.lat, req.body.long)
    Article.find({
        $or: [
            {content: {$regex: req.body.searchbox, $options: 'i'}},
            {
                title: {$regex: req.body.searchbox, $options: 'i'}
        }]
    }).near('location', {center: [req.body.long, req.body.lat], spherical: true}).exec(function (err, collection) {
        if (err) throw err;
        res.send(collection);
    })
};