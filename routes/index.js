var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
   res.locals.stuff = {
       query : req.query,
       url   : req.originalUrl
   }
  res.render(
	  'index',
	  { title: 'DWS Calendar' });
});

module.exports = router;
