        

        async function authenticate() {
            const tg = window.Telegram.WebApp;

            tg.ready();

            tg.expand();


            const initData = tg.initData;

            if (!initData) {

                document.getElementById("status").innerText =
                    "Please open this application from Telegram.";

                return;
            }


            try {

                const response = await fetch("/telegram_login/", {

                    method: "POST",

                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": "{{ csrf_token }}"
                    },

                    body: JSON.stringify({
                        init_data: initData
                    })

                });


                const data = await response.json();


                if (!response.ok) {

                    document.getElementById("status").innerText =
                        data.error || "Authentication failed.";

                    console.error(data);

                    return;
                }


                if (data.success) {

                    window.location.href = "/dashboard/";

                    console.log("Authenticated user:", data.user);

                }

            } catch (error) {

                console.error(error);

                document.getElementById("status").innerText =
                    "Unable to connect to the server.";

            }

        }


        authenticate();