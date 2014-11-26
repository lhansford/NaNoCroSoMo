$( document ).ready(function() {
  resetMessage();
  $('#form').submit(function() {
    return false;
  });
  $('#word-input').keypress(function (e) {
    if (e.which == 13) {
      addWord();
    }
  });
  $("#word-input").focus();
  $("#add-word").click( function() {
    addWord();
  });
});

function addWord (){
  resetMessage();
  var word = $.trim($("#word-input").val());
  if (checkWord(word)){
    var paragraph = false;
    if (isEndOfSentence(word)){
      paragraph = confirmEndOfParagraph();
    }
    var payload = {
      "word": word,
      "paragraph": paragraph,
      "story_id": storyId,
      "timestamp": loadTimestamp
    };
    $.post( "_add", JSON.stringify(payload), function( data ) {
      console.log(data);
      loadTimestamp = data.timestamp;
      loadNewData(data.paragraphs);
      $("#word-input").val('');
      $("#word-input").focus();
    }, 'json');
  }
}

function checkWord (word) {
  if(word.length < 1){
    flashMessage("You need to type a word.");
    return false;
  }
  if(word.indexOf(' ') === -1){
      return true;
  }
  flashMessage("Words cannot contain spaces.");
  return false;
}

function loadNewData(paragraphs){
  // Append text of first array element to last <p>
  if(paragraphs.length > 0){
    var last = $('.story p:last-child');
    last.text(last.text() + " " + paragraphs[0]);
  }
  // Create new <p> for all other array elements
  for(var i = 1; i < paragraphs.length; i++){
    $('.story').append("<p>" + paragraphs[i] + "</p>");
  }
}

function flashMessage(message){
  $('#error').show();
  $('#error').text(message);
}

function resetMessage(){
  $('#error').hide();
}

function confirmEndOfParagraph(){
  return confirm("Start a new paragraph?");
}

function isEndOfSentence(word){
  var lastChar = word[word.length - 1];
  if( lastChar === '.' || lastChar === '!' || lastChar === '?'){
    return true;
  }
  return false;
}
