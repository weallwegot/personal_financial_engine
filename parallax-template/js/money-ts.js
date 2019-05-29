/*global WildRydes _config AmazonCognitoIdentity AWSCognito*/
var WildRydes = window.WildRydes || {};


(function rideScopeWrapper($) {
    var authToken;
    WildRydes.authToken.then(function setAuthToken(token) {
        if (token) {
            authToken = token;
        } else {
            window.location.href = '/signin.html';
        }
    }).catch(function handleTokenError(error) {
        // take user back to signin if token is not handled
        alert(error);
        window.location.href = '/signin.html';
    });

    function requestMoneyTimeseries() {
        $.ajax({
            method: 'POST',
            url: _config.api.invokeUrl + '/moneytimeseries',
            headers: {
                Authorization: authToken
            },
            data: JSON.stringify({
                Onward: {
                    TestPacket1: 12.04,
                    TestPacket2: 1906
                }
            }),
            contentType: 'application/json',
            success: completeRequest,
            error: function ajaxError(jqXHR, textStatus, errorThrown) {
                console.error('Error requesting ride: ', textStatus, ', Details: ', errorThrown);
                console.error('Response: ', jqXHR.responseText);
                alert('An error occured when requesting your money trend:\n' + jqXHR.responseText);
            }
        });
    }

    // complete the request by taking the timeseries data returned and using it to populate the timeseries plot
    function completeRequest(result) {
        console.log('Response received from API: ',result)

        var trace1 = {
          x: [1, 2, 3, 4],
          y: [10, 15, 13, 17],
          type: 'scatter'
        };

        var trace2 = {
          x: [1, 2, 3, 4],
          y: [16, 5, 11, 9],
          type: 'scatter'
        };

        var data = [trace1, trace2];

        Plotly.newPlot("money-ts-line-plot", data);
    }

    // Register click handler for #signout button
    $(function onDocReady() {

        $('#signOut').click(function() {
            WildRydes.signOut();
            alert("You have been signed out.");
            window.location = "signin.html";
        });
        requestMoneyTimeseries();

        WildRydes.authToken.then(function updateAuthMessage(token) {
            if (token) {
                displayUpdate('You are authenticated. Click to see your <a href="#authTokenModal" data-toggle="modal">auth token</a>.');
                $('.authToken').text(token);
            }
        });

        if (!_config.api.invokeUrl) {
            $('#noApiMessage').show();
        }
    });

    function displayUpdate(text) {
        $('#updates').append($('<li>' + text + '</li>'));
    }
}(jQuery));
