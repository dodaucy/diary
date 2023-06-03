function logout_all_sessions(element) {
    if (!confirm(element)) {
        return;
    }
    disable(true);
    request(
        "POST",
        "logout_all",
        function() {
            location.reload();
        },
        function() {
            reset_confirmations();
            disable(false);
        }
    );
}
