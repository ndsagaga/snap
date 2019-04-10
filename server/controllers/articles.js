var Article = require('mongoose').model('Article');

exports.getArticles = function (req, res) {
    Article.find({}).exec(function (err, collection) {
        res.send(collection);
    })
};

exports.getArticlesForQuery = function (req, res) {
    Article.find({
        $or: [{content: {$regex: req.params.query, $options: 'i'}}, {
            title: {
                $regex: req.params.query,
                $options: 'i'
            }
        }]
    }).exec(function (err, collection) {
        res.send(collection);
    })
};

exports.getArticlesForQueryWithLocation = function (req, res) {
    Article.find({
        $or: [{content: {$regex: req.params.query, $options: 'i'}}, {
            title: {
                $regex: req.params.query,
                $options: 'i'
            }
        }]
    }).exec(function (err, collection) {
        res.send(collection);
    })
};