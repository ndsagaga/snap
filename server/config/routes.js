var articles = require('../controllers/articles'),
    images = require('../controllers/images'),
    mongoose = require('mongoose'),
    path = require('path');

module.exports = function (app) {

    app.get('/view/:file', function (req, res) {
        res.sendFile(path.join(__dirname + '/../views/') + req.params.file);
    });

    app.get('/res/:folder/:file', function (req, res) {
        res.sendFile(path.join(__dirname + '/../res/') + req.params.folder + '/' + req.params.file);
    });

    app.post('/search', articles.getArticlesForQueryWithLocation);

    app.get('/api/articles', articles.getArticles);
    app.get('/api/articles/:query', articles.getArticlesForQueryWithLocation);
    app.get('/api/article/:id', articles.getArticlesById);

    app.post('/api/article/:id/comment', articles.addCommentToArticle);

    app.get('/api/image/:image', images.getImage);

    app.all('/api/location', function (req, res) {
        var ip = req.connection.remoteAddress ||
            req.socket.remoteAddress ||
            (req.connection.socket ? req.connection.socket.remoteAddress : null);

        res.send(ip)
    });

    app.all('/api/*', function (req, res) {
        res.send(404);
    });

    app.get('*', function (req, res) {
        res.render('index', {
            bootstrappedUser: req.user
        });
    });
};