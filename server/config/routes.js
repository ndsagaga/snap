var articles = require('../controllers/articles'),
    mongoose = require('mongoose');

module.exports = function (app) {
    app.get('/api/articles', articles.getArticles);
    app.get('/api/articles/:query', articles.getArticlesForQuery);

    app.get('/partials/*', function (req, res) {
        res.render('../../public/app/' + req.params[0]);
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