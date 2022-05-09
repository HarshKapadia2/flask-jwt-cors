const errorDiv = document.querySelector("#error");
const form = document.querySelector("form");

window.addEventListener("load", () => {
	const token = localStorage.getItem("flaskJwtTest");

	if (!token) return;

	fetch("http://127.0.0.1:5000/isAuthorized", {
		method: "GET",
		mode: "cors",
		headers: {
			"Accept": "application/json",
			"Authorization": `Bearer ${token}`
		},
		credentials: "include"
	})
		.then((response) => {
			if (response.status === 200) window.location = "/protected.html";
			else if (response.status === 401)
				localStorage.removeItem("flaskJwtTest");
			else throw new Error(`${response.status} ${response.statusText}`);
		})
		.catch((err) => console.error("Fetch error: ", err));
});

form.addEventListener("submit", (event) => {
	event.preventDefault();

	const userData = {
		username: form.elements["username"].value,
		password: form.elements["password"].value
	};

	fetch("http://127.0.0.1:5000/login", {
		method: "POST",
		mode: "cors",
		headers: {
			"Content-Type": "application/json",
			"Accept": "application/json"
		},
		body: JSON.stringify(userData)
	})
		.then((response) => {
			if (response.status === 200) return response.json();
			else if (response.status === 401) {
				errorDiv.innerText = "Invalid username and/or password.";
				errorDiv.style.color = "red";
				throw new Error("Invalid username and/or password.");
			} else throw new Error(`${response.status} ${response.statusText}`);
		})
		.then((data) => {
			if (data.message === "Success") {
				localStorage.setItem("flaskJwtTest", data.token);
				window.location = "/protected.html";
			} else throw new Error(data.message);
		})
		.catch((err) => {
			console.error("Fetch error: ", err);
		});
});
