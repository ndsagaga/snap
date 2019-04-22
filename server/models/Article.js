var mongoose = require('mongoose');
var GeoJSON = require('mongoose-geojson-schema');

var articleSchema = mongoose.Schema({
    id: {type: Number, required: '{PATH} is required!'},
    title: {type: String, required: '{PATH} is required!'},
    imageUrl: {type: String, required: '{PATH} is required!'},
    url: {type: String, required: '{PATH} is required!'},
    content: {type: String, required: '{PATH} is required!'},
    author: {type: String, required: '{PATH} is required!'},
    readMoreUrl: {type: String, required: '{PATH} is required!'},
    location: mongoose.Schema.Types.MultiPoint,
    timestamp: {type: Number, required: '{PATH} is required!'},
}, {strict: false});

articleSchema.index({location: "2dsphere"});
articleSchema.index({title: "text", content: "text"});
var Article = mongoose.model('Article', articleSchema, 'Article');