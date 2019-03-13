function update(){
	fetch('/data')
	.then((resp) => resp.json())
	.then(function(data) {
		var elements = document.querySelectorAll('.tweet_image');
		Array.prototype.forEach.call(elements, function(el, i){
			el.src = data.images[i]
		})
		document.querySelector('#tweets_per_hour').innerHTML = data.tweets_per_hour.toString()
		document.querySelector('#men_per_hour').innerHTML = data.men_per_hour.toString()
		document.querySelector('#women_per_hour').innerHTML = data.women_per_hour.toString()
	})
}

function post(){
	fetch('/post', {
		method: 'POST',
		headers: new Headers(),
		body: JSON.stringify({'track':document.querySelector('#terms').value.split(' ')})
	})
	.then(function(){
		document.querySelector('#terms').value = '';
	})
}

window.onload = function(){
	document.querySelector('#submit_terms').onclick = post;
	update()
	setInterval(update, 5000)
}