var articles = require('../controllers/articles'),
    images = require('../controllers/images'),
    mongoose = require('mongoose');

module.exports = function (app) {
    app.get('/api/articles', articles.getArticles);
    app.get('/api/articles/:query', articles.getArticlesForQueryWithLocation);

    app.get('/partials/*', function (req, res) {
        res.render('../../public/app/' + req.params[0]);
    });

    app.get('/api/image/:image', images.getImage);
    app.get('/api/images', images.getAllImages);

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
        var ip = req.connection.remoteAddress ||
            req.socket.remoteAddress ||
            (req.connection.socket ? req.connection.socket.remoteAddress : null);
        console.log("WRONG API: " + ip)
        res.render('index', {
            bootstrappedUser: req.user
        });
    });
};