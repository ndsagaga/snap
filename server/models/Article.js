var mongoose = require('mongoose');

var articleSchema = mongoose.Schema({
    id: {type: Number, required: '{PATH} is required!'},
    title: {type: String, required: '{PATH} is required!'},
    imageUrl: {type: String, required: '{PATH} is required!'},
    url: {type: String, required: '{PATH} is required!'},
    content: {type: String, required: '{PATH} is required!'},
    author: {type: String, required: '{PATH} is required!'},
    readMoreUrl: {type: String, required: '{PATH} is required!'},
    location: {
        type: {
            type: String,
            enum: ['MultiPoint'],
            required: true
        },
        coordinates: {
            type: [[Number]],
            required: true
        }
    },
    timestamp: {type: Date, required: '{PATH} is required!'},
});
var Article = mongoose.model('Article', articleSchema);