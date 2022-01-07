const auto_refresh_interval = 60000;

const channel_html = (channel) => `
<div class="stats-channel">
    <h5 class="stats-channel-name">
        <a target="_blank" href="https://emnlp2020.rocket.chat/channel/${channel.name}">#${channel.name}</a>
    </h5>
    <span class="stats-channel-info text-muted"  tabindex="0" data-toggle="tooltip" 
        data-placement="bottom" title="Number of Users"><i class="fas fa-users"></i> ${channel.usersCount}</span> 
    &nbsp;
    &nbsp;
    <span class="stats-channel-info text-muted"  tabindex="0" data-toggle="tooltip" 
        data-placement="bottom" title="Number of Total Messages"><i class="fas fa-comments"></i> ${channel.msgs}</span> 
    &nbsp;
    &nbsp;
    <span class="stats-channel-info text-success"  tabindex="0" data-toggle="tooltip" 
        data-placement="bottom" title="Number of New Messages"><i class="fas fa-chart-line"></i> ${channel.diff}</span> 
    &nbsp;
    &nbsp;
    <span class="stats-channel-info text-muted">
        <a target="_blank" href="https://emnlp2020.rocket.chat/channel/${channel.name}">Open this chat</a>
    </span> 
</div>
`;

const render_stats = (stats_obj) => {
  $("#highly-active-chats-progress-bar").hide();
  $("#highly-active-chats-btn-refresh").show();
  $("#highly-active-chats-btn-refresh").prop("disabled", false);

  list_html = stats_obj.stats.map((s) => channel_html(s.channel));
  $("#highly-active-chats-list").html(list_html);

  last_update = moment
    .unix(stats_obj.last_update)
    .local()
    .format("MMM Do, HH:mm:ss");
  last_update_html = `Last update: ${last_update} (Refreshes every ${
    auto_refresh_interval / 1000
  }s)`;
  $("#highly-active-chats-last-update").html(last_update_html);
  setTimeout(() => $('[data-toggle="tooltip"]').tooltip(), 0);
};

const load_stats = () => {
  path_to_stats_json = `${channel_stats_server}/stats.json`;
  d3.json(path_to_stats_json)
    .then((stats) => {
      render_stats(stats);
      setTimeout(load_stats, auto_refresh_interval);
    })
    .catch((e) => {
      console.error(e);
      setTimeout(load_stats, auto_refresh_interval);
    });
};

$("#highly-active-chats-btn-refresh").click(() => {
  $("#highly-active-chats-last-update").html("");
  $("#highly-active-chats-list").html("");
  $("#highly-active-chats-progress-bar").show();
  $("#highly-active-chats-btn-refresh").hide();

  setTimeout(load_stats, 0);
});
