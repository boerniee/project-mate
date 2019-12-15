function validatePassword(password) {
    if (password.length === 0) {
        document.getElementById("msg").innerHTML = "";
        return -1;
    }
    var matchedCase = new Array();
    matchedCase.push("[$@$§!%*#?&]");
    matchedCase.push("[A-Z]");
    matchedCase.push("[0-9]");
    matchedCase.push("[a-z]");

    var ctr = 0;
    for (var i = 0; i < matchedCase.length; i++) {
        if (new RegExp(matchedCase[i]).test(password)) {
            ctr++;
        }
    }
    if (password.length < 5) {ctr = 0;}
    var color = "";
    var strength = "";
    return ctr;
}

function togglePassword() {
  pwd = $('#password')
  if (pwd.attr('type') === 'password') {
    pwd.attr('type', 'text');
  } else {
    pwd.attr('type', 'password');
  }
}
