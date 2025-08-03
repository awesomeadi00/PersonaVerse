$(document).ready(function () {
    let selectedPersonality = "Helpful Mom";
    let conversationHistories = {};

    function scrollToBottom() {
        $('.chat-box').scrollTop($('.chat-box')[0].scrollHeight);
    }

    function updateChatBox() {
        const messages = conversationHistories[selectedPersonality] || [];
        $('.chat-box').empty();
        messages.forEach(msg => {
            const messageClass = msg.type === 'user' ? 'message user' : 'message ai';
            $('.chat-box').append('<div class="' + messageClass + '"><div class="message-content">' + msg.content + '</div></div>');
        });
        scrollToBottom();
    }

    function loadUserChats() {
        $.get('/load_chats', { user_id: currentUserID }, function (response) {
            if (response.error) {
                console.error(response.error);
                return;
            }
            conversationHistories = response;
            updateChatBox();
        });
    }

    function selectPersonality(personality) {
        selectedPersonality = personality;
        $('.sidebar-item, .dropdown-content a').removeClass('active');
        $('.sidebar-item, .dropdown-content a').filter(function () {
            return $(this).data('personality') === personality;
        }).addClass('active');
        $('.chat-title').text(selectedPersonality);
        updateChatBox();
        $('.dropdown-content').hide(); // Hide the dropdown content
    }

    $('.sidebar-item, .dropdown-content a').click(function () {
        let personality = $(this).data('personality');
        selectPersonality(personality);
    });

    $('.message-form').on('submit', function (e) {
        e.preventDefault();
        let userInput = $('#user_input').val();
        $('#user_input').val('');
        if (userInput.trim() !== '') {
            let userMessage = { type: 'user', content: userInput };
            if (!conversationHistories[selectedPersonality]) {
                conversationHistories[selectedPersonality] = [];
            }
            conversationHistories[selectedPersonality].push(userMessage);
            updateChatBox();
            $.post('/get_response', { user_input: userInput, personality: selectedPersonality }, function (response) {
                let aiMessage = { type: 'ai', content: response };
                conversationHistories[selectedPersonality].push(aiMessage);
                updateChatBox();
            });
        }
    });

    loadUserChats(); // Load chats when the document is ready

    $('.dropdown .dropbtn').click(function () {
        $(this).next('.dropdown-content').show();
    });

    $('.user-dropdown .dropbtn-menu').click(function () {
        $(this).next('.dropdown-content-user').show();
    });

    $(document).click(function (event) {
        if (!$(event.target).closest('.dropdown, .user-dropdown').length) {
            $('.dropdown-content, .dropdown-content-user').hide();
        }
    });

    $('.dropdown-content, .dropdown-content-user').click(function (e) {
        e.stopPropagation();
    });

    // Function to show the modal
    function showModal() {
        $('#confirmation-modal').show();
    }

    // Function to hide the modal
    function hideModal() {
        $('#confirmation-modal').hide();
    }

    // Click handler for "Clear Chat" button
    $('#clear-chat').click(function () {
        showModal();
    });

    // Click handler for "No" button in modal
    $('#cancel-clear').click(function () {
        hideModal();
    });

    // Click handler for "Yes" button in modal
    $('#confirm-clear').click(function () {
        $.post('/clear_chats', { user_id: currentUserID }, function (response) {
            if (response.status === "success") {
                conversationHistories = {};
                updateChatBox();
                hideModal();
            } else {
                console.error('Failed to clear chats:', response.error);
            }
        });
    });

    // Click handler for close button in modal
    $('.close').click(function () {
        hideModal();
    });
});
