/*
#terms
#submit_terms

.tweet_images
.tweet_image

#tweets_per_hour
#men_per_hour
#women_per_hour
*/

function update()
{
	fetch('/data')
	.then((resp) => resp.json())
	.then(function(data) {
		var elements = document.querySelectorAll('.tweet_image');
		Array.prototype.forEach.call(elements, function(el, i){
			el.src = data.images[i]
		})
		document.querySelector('#tweets_per_hour').innerHTML = data.tweets_per_hour.toString()
		document.querySelector('#men_per_hour').innerHTML = data.men_per_hour.toString()
		document.querySelector('#women_per_hour').innerHTML = data.men_per_hour.toString()
	})
}

window.onload = function(){
	update()
	setInterval(update, 5000)
}