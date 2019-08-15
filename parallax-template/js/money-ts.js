/*global WildRydes _config AmazonCognitoIdentity AWSCognito*/
var WildRydes = window.WildRydes || {};

(function rideScopeWrapper($) {
    var authToken;
    WildRydes.authToken
        .then(function setAuthToken(token) {
            if (token) {
                authToken = token;
            } else {
                window.location.href = "/signin.html";
            }
        })
        .catch(function handleTokenError(error) {
            // take user back to signin if token is not handled
            alert(error);
            window.location.href = "/signin.html";
        });

    function requestMoneyTimeseries() {
        $.ajax({
            method: "POST",
            url: _config.api.invokeUrl + "/moneytimeseries",
            headers: {
                Authorization: authToken
            },
            data: JSON.stringify({
                Onward: {
                    TestPacket1: 12.04,
                    TestPacket2: 1906
                }
            }),
            contentType: "application/json",
            success: completeRequest,
            error: function ajaxError(jqXHR, textStatus, errorThrown) {
                console.error(
                    "Error requesting ride: ",
                    textStatus,
                    ", Details: ",
                    errorThrown
                );
                console.error("Response: ", jqXHR.responseText);

                $("#modal-money-ts-error-help").modal("open")

                // alert(
                //     "An error occured when requesting your money trend:\n" +
                //         jqXHR.responseText
                // );
            }
        });
    }

    // complete the request by taking the timeseries data returned and using it to populate the timeseries plot
    function completeRequest(result) {
        console.log("Response received from API: ", result);

        var forecastedMoneyResult = result.forecastData

        var dates = forecastedMoneyResult.map(x => x.date);
        var totals = forecastedMoneyResult.map(x => x.daily_total);

        var accounts = Object.keys(forecastedMoneyResult[0]).filter(
            i =>
                !i.endsWith("transactions") && i != "date" && i != "daily_total"
        );
        var account_balances = {};
        var idx;
        // calculate totals for each account name
        for (idx in accounts) {
            var accName = accounts[idx];
            var accDailyBalances = forecastedMoneyResult.map(x => x[accName]);
            var accDailyTxs = forecastedMoneyResult.map(x => x[accName + "transactions"]);
            account_balances[accName] = {
                x: dates,
                y: accDailyBalances,
                name: accName,
                text: accDailyTxs,
                type: "scatter"
            };
        }

        var totals_trace = {
            x: dates,
            y: totals,
            name: "Totals",
            type: "scatter"
        };

        var data = [totals_trace];

        Plotly.newPlot(
            "money-ts-line-plot",
            data.concat(Object.values(account_balances))
        );
    }

    // Register click handler for #signout button
    $(function onDocReady() {
        $("#signOut").click(function() {
            WildRydes.signOut();
            alert("You have been signed out.");
            window.location = "signin.html";
        });


        var modal_elems = document.querySelectorAll('.modal')
        M.Modal.init(modal_elems,{})

        requestMoneyTimeseries();

        WildRydes.authToken.then(function updateAuthMessage(token) {
            if (token) {
                displayUpdate(
                    'You are authenticated. Click to see your <a href="#authTokenModal" data-toggle="modal">auth token</a>.'
                );
                $(".authToken").text(token);
            }
        });

        if (!_config.api.invokeUrl) {
            $("#noApiMessage").show();
        }
    });

    function displayUpdate(text) {
        $("#updates").append($("<li>" + text + "</li>"));
    }
})(jQuery);
