const username = document.querySelector("#username");
const nameDiv = document.querySelector("#name");
const logOutBtn = document.querySelector("button");

window.addEventListener("load", () => {
	const token = localStorage.getItem("flaskJwtTest");

	if (!token) {
		window.location = "/login.html";
		return;
	}

	fetch("http://127.0.0.1:5000/protected", {
		method: "GET",
		mode: "cors",
		headers: {
			"Accept": "application/json",
			"Authorization": `Bearer ${token}`
		},
		credentials: "include"
	})
		.then((response) => {
			if (response.status === 200) return response.json();
			else if (response.status === 401) {
				localStorage.removeItem("flaskJwtTest");
				window.location = "/login.html";
			} else throw new Error(`${response.status} ${response.statusText}`);
		})
		.then((data) => {
			username.innerText = data.username;
			nameDiv.innerText = data.name;
		})
		.catch((err) => console.error("Fetch error: ", err));
});

logOutBtn.addEventListener("click", () => {
	localStorage.removeItem("flaskJwtTest");
	window.location = "/";
});
