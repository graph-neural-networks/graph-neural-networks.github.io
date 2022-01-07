let allPapers = [];
const allKeys = {
    authors: [],
    keywords: [],
    session: [],
    titles: [],
}
const filters = {
    authors: null,
    keywords: null,
    session: null,
    title: null,
};
let path_to_papers_json = "";
let render_mode = 'list';
let current_card_index = -1;

const removeOldFocus = () => {
    if (current_card_index !== -1) {
        $('.card-paper').eq(current_card_index).removeClass('card-active')
    }
}

const updateCardIndex = (card_index) => {
    removeOldFocus()

    if (card_index < -1) return;

    current_card_index = card_index;
    if (current_card_index == -1) return;

    let card = $('.card-paper').eq(current_card_index)
    
    card.addClass('card-active');
    // $('.card-paper').eq(current_card_index).focus();

    if (!card.visible()) {
        var $window = $(window),
        $element = card;
        elementTop = $element.offset().top,
        elementHeight = $element.height(),
        viewportHeight = $window.height(),
        scrollIt = elementTop - ((viewportHeight - elementHeight) / 2);

        // $window.scrollTop(scrollIt);
        $("html, body").animate({ scrollTop: scrollIt }, 50);
    }

    let isShown = ($("#quickviewModal").data('bs.modal') || {})._isShown;
    if (isShown) 
        $('.card-paper').eq(current_card_index).find(".btn-quickview")[0].click();
}

const setUpKeyBindings = () => {

    Mousetrap.bind('right', () => {
        if (current_card_index >= $('.card-paper').length - 1) 
            return;
        
        updateCardIndex(current_card_index+1);
    });

    Mousetrap.bind('left', () => {
        if (current_card_index <= 0) 
            return;
        
        updateCardIndex(current_card_index-1);
    });

    Mousetrap.bind('space', () => {
        if (current_card_index == -1)
            return

        let isShown = ($("#quickviewModal").data('bs.modal') || {})._isShown
        if (isShown) 
            $('#quickviewModal').modal('toggle')
        else
            $('.card-paper').eq(current_card_index).find(".btn-quickview")[0].click()
    })

    Mousetrap.bind('esc', () => {
        let isShown = ($("#quickviewModal").data('bs.modal') || {})._isShown
        if (isShown) {
            $('#quickviewModal').modal('hide')
            return;
        }
        
        updateCardIndex(-1);
    })

    Mousetrap.bind('f', () => {
        if (current_card_index == -1)
            return;

        let isShown = ($("#quickviewModal").data('bs.modal') || {})._isShown;
        if (isShown) 
            $('#modalFavBtn').click();
        else
            $('.card-paper').eq(current_card_index).find(".btn-fav")[0].click();
    })

    
    Mousetrap.bind('enter', () => {
        if (current_card_index == -1)
            return;

        let isShown = ($("#quickviewModal").data('bs.modal') || {})._isShown;
        if (isShown) {
            $('#modalPaperPage').click();
        } else {
            let title = $('.card-paper').eq(current_card_index).find(".card-title")[0];
            title.click();
            window.open(title.attr('href'), '_blank');
        }
    })
}

const persistor = new Persistor('Mini-Conf-Papers');
const favPersistor = new Persistor('Mini-Conf-Favorite-Papers');

const updateTrackList = (tracks, selected_track) => {
    let optionsHtml = tracks.map(track_html);

    $('#track_selector').html(optionsHtml).selectpicker("refresh");
    $('#track_selector').val(selected_track).selectpicker("refresh");
}

const updateCards = (papers) => {
    const storedPapers = persistor.getAll();
    const favPapers = favPersistor.getAll();
    
    papers.forEach(
      openreview => {
          openreview.content.read = storedPapers[openreview.id] || false
          openreview.content.isFav = favPapers[openreview.id] || false
      })

    papers.map((e, idx, array) => {
        e.index_in_list = idx;
        return e;
    })

    const readCard = (iid, new_value) => {
        persistor.set(iid, new_value);
        // storedPapers[iid] = new_value ? 1 : null;
        // Cookies.set('papers-selected', storedPapers, {expires: 365});
    }

    const favPaper = (iid, new_value) => {
        favPersistor.set(iid, new_value);
    }
    
    
    $('#progressBar').hide();

    const all_mounted_cards = d3.select('.cards')
      .selectAll('.myCard', openreview => openreview.id)
      .data(papers, d => d.number)
      .join('div')
      .attr('class', 'myCard col-xs-6 col-md-4')
      .html(card_html)

    all_mounted_cards.select('.card-title')
      .on('click', function (d) {
          const iid = d.id;
          all_mounted_cards.filter(d => d.id === iid)
            .select(".card-title").classed('card-title-visited', function () {
              const new_value = true;//!d3.select(this).classed('not-selected');
              readCard(iid, new_value);
              return new_value;
          })
      })

    all_mounted_cards.select('.btn-quickview')
      .on('click', function (d) {
          const iid = d.id;
          updateCardIndex(d.index_in_list)
          openQuickviewModal(d);
          d3.event.stopPropagation();
      })

    all_mounted_cards.select(".btn-fav")
      .on('click', function (d) {
          const iid = d.id;
          let btn = d3.select(this)
          const is_fav = btn.classed('btn-warning');
          
          if (is_fav) {
            btn.classed('btn-warning', false)
            btn.classed('btn-outline-primary', true)
            btn.html('<i class="fas fa-star"></i> Add to Favorites')
            $(btn.node()).tooltip('dispose')
            $(btn.node()).parent().parent().removeClass('card-fav')
          } else {
            btn.classed('btn-warning', true)
            btn.classed('btn-outline-primary', false)
            btn.html('<i class="fas fa-star"></i>')
            $(btn.node()).tooltip(
                {title:'Click to remove from Favorites', placement: 'left'})
            $(btn.node()).parent().parent().addClass('card-fav')
          }

          favPaper(iid, !is_fav)
      })

    
    $('[data-toggle="tooltip"]').tooltip()

    lazyLoader();
}

const openQuickviewModal = (paper) => {
    updateModalData(paper);
    $('#quickviewModal').modal('show')
}

const maybe_update = (element_ids, value, callback) => {
    if (value && (
        (typeof value == "string" && value !== "") ||
        (Array.isArray(value) && value.length > 0 )))
        element_ids.forEach(x => $(x).show());
    else
        element_ids.forEach(x => $(x).hide());

    callback(value);
}

const updateModalData = (paper) => {

    let program = paper.content.program;
    let badgeClass = program_to_badge_class[program];
    $('#modalTitle').html(
        `${paper.content.title} &nbsp; <span class="badge badge-pill badge-${badgeClass}">${program}</span>`);

    let isVisited = persistor.get(paper.id) || false
    if (isVisited)
        $('#modalTitle').addClass('card-title-visited');
    else
        $('#modalTitle').removeClass('card-title-visited');

    let authorsHtml = paper.content.authors.map(author_html).join(', ');
    maybe_update(
        ["#modalAuthors"], 
        authorsHtml,
        x => $('#modalAuthors').html(x));

    
    maybe_update(
        ['#modalPaperType'], 
        paper.content.paper_type,
        x => $('#modalPaperType').text(x));
    maybe_update(
        ['#modalPaperTrack'], 
        paper.content.track,
        x => $('#modalPaperTrack').text(x));

    maybe_update(
        ['#modalAbstract', '#modalAbstractHeader'], 
        paper.content.abstract,
        x => $('#modalAbstract').text(x));
    
    if (program != "workshop"){
        $('#modalChatUrl').attr('href', `https://${chat_server}/channel/paper-${paper.id.replace('.', '-')}`);
        $('#modalPaperPage').attr('href', `paper_${paper.id}.html`);
    } else {
        $('#modalChatUrl').hide();
        $('#modalPaperPage').hide();
    }
    
    maybe_update(
        ['#modalPresUrl'], 
        paper.presentation_id,
        x => $('#modalPresUrl').attr('href', `https://slideslive.com/${x}`));
    maybe_update(
        ['#modalPaperUrl'], 
        paper.content.pdf_url,
        x => $('#modalPaperUrl').attr('href', x));
    

    let keywordsHtml = paper.content.keywords.map(modal_keyword).join('\n');
    maybe_update(
        ['#modalKeywords', '#modalKeywordsHeader'], 
        paper.content.keywords,
        x => $('#modalKeywords').html(keywordsHtml));

    let sessionsHtml = paper.content.sessions.map(s => modal_session_html(s, paper)).join('\n');
    $('#modalSessions').html(sessionsHtml);
    maybe_update(
        ['#modalSessions', '#modalSessionsHeader'], 
        paper.content.sessions,
        x => $('#modalSessions').html(sessionsHtml));

    $('#modalPaperPage').unbind( "click" );
    $('#modalPaperPage').click(() => {
        $('.card-title').eq(current_card_index).click();
        $('#modalTitle').addClass('card-title-visited');
    });

    let favBtn = $('#modalFavBtn')

    const updateFavBtn = (isFav) => {
        if (isFav) {
            favBtn.removeClass('btn-outline-primary')
            favBtn.addClass('btn-warning')
            favBtn.html('<i class="fas fa-star"></i>')
            favBtn.tooltip(
                {title:'Click to remove from Favorites', placement: 'left'})
        } else {
            favBtn.removeClass('btn-warning')
            favBtn.addClass('btn-outline-primary')
            favBtn.html('<i class="fas fa-star"></i> Add to Favorites')
            favBtn.tooltip('dispose')
        }
    }

    updateFavBtn(favPersistor.get(paper.id));

    favBtn.unbind( "click" );
    favBtn.click(() => {
        $('.btn-fav').eq(current_card_index).click();
        updateFavBtn(favPersistor.get(paper.id))
    })

    $('#quickviewModal').modal('handleUpdate');
}

const moveArrayItem = (array, fromIndex, toIndex) => {
    const arr = [...array];
    arr.splice(toIndex, 0, ...arr.splice(fromIndex, 1));
    return arr;
}

function sortSelectedFirst(array) {
    const selections = Object.keys(persistor.getAll())
    for (let i = array.length - 1; i > 0 ; i--) {
        if (selections.includes(array[i].id)) {
            array = moveArrayItem(array, i, 0)
        }
    }
    allPapers = array;
}

/* Randomize array in-place using Durstenfeld shuffle algorithm */
function shuffleArray(array) {

    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        const temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
}

function hideQaEnded(array, element){
    if (element.checked) {
        let result = []
        let now = new Date()
        for (let i = array.length - 1; i > 0; i--) {
            let qa = new Date(Math.max.apply(null, array[i].content.sessions.map(function (e) {
                return new Date(e.end_time);
            })));
            if (qa.getTime() >= now.getTime())
                result.push(array[i])
        }
        allPapers = result;

        render()
    } else {
        // reload full list of papers from data
        d3.json(path_to_papers_json).then(papers => {
            shuffleArray(papers);
            allPapers = papers;
            render()
        }).catch(e => console.error(e));
    }
}

const render = () => {
    current_card_index = -1;

    $('.cards').empty();
    $('#progressBar').show();

    const f_test = [];
    
    const showFavs = getUrlParameter("showFavs") || '0';
    const favPapers = favPersistor.getAll();

    const urlFilter = getUrlParameter("filter") || 'titles';
    const urlSearch = getUrlParameter("search");
    // console.log(urlSearch);
    if ((urlSearch !== '') || updateSession()) {
        filters[urlFilter] = urlSearch;
        $('.typeahead_all').val(urlSearch);
    }

    updateSession();

    Object.keys(filters)
      .forEach(k => {filters[k] ? f_test.push([k, filters[k]]) : null})

     // console.log(f_test, filters, "--- f_test, filters");
    if (f_test.length === 0 && showFavs != '1') {
        // $('#progressBar').hide();
        setTimeout(()=>{updateCards(allPapers)}, 50);
    } else {
        setTimeout(()=>{
            const fList = allPapers.filter(
            d => {
                let pass_test = true;

                if (showFavs === '1')
                    pass_test &= favPapers[d.id];

                let i = 0;
                while (i < f_test.length && pass_test) {
                    if (f_test[i][0] === 'titles') {
                        var d_content = "";
                        if(d.content["title"].indexOf("+")!=-1){
                            d_content = d.content['title'].replace("\+\+","  ");
                        }else{
                            d_content = d.content['title'];
                        }
                        pass_test &= d_content.toLowerCase()
                            .indexOf(f_test[i][1].toLowerCase()) > -1;

                    } else {
                        if (f_test[i][0] === 'session' || f_test[i][0] === 'sessions' ) {
                            pass_test &= d.content['sessions'].some(
                                function (item) {
                                    return item.session_name === f_test[i][1];
                                }
                            );
                        } else {
                            pass_test &= d.content[f_test[i][0]].indexOf(
                                f_test[i][1]) > -1
                        }
                    }
                    i++;
                }
                return pass_test;
            });
            // console.log(fList, "--- fList");
            
            updateCards(fList)
        }, 50);
    }
}

const updateFilterSelectionBtn = value => {
    d3.selectAll('.filter_option label')
      .classed('active', function () {
          const v = d3.select(this).select('input').property('value')
          return v === value;
      })
}

const updateSession = () => {
    const urlSession = getUrlParameter("session");
    let sessionName;
    if (urlSession) {
        filters['session'] = urlSession;
        // special processing for regular QA session and Demo session
        if (urlSession.startsWith("D")) {
          sessionName = "Demo Session " + urlSession.substring(1)
        } else {
          sessionName = "Session " + urlSession
        }
        d3.select('#session_name').text(sessionName);
        d3.select('.session_notice').classed('d-none', null);
        return true;
    } else {
        filters['session'] = null
        return false;
    }
}

const updateToolboxUI = (program, urlFilter, track) =>{
    updateFilterSelectionBtn(urlFilter);

    // Update program selector UI
    document.querySelector(`input[name=program][value=${program}]`).checked = true;

    $("#track_selector").selectpicker('hide');
    $("#track_selector_placeholder").addClass("d-lg-block");
    // if (["main", "workshop"].includes(program)) {
    //     $("#track_selector").selectpicker('show');
    //     $("#track_selector_placeholder").removeClass("d-lg-block");
    // } else{
    //     $("#track_selector").selectpicker('hide');
    //     $("#track_selector_placeholder").addClass("d-lg-block");
    // }
}

/**
 * START here and load JSON.
 */
const start = (reset_track) => {
    
    reset_track = reset_track || false;

    const urlFilter = getUrlParameter("filter") || 'titles';
    const program = getUrlParameter("program") || 'Main'
    let default_track = program == "workshop"? "All workshops" : "All tracks";

    let track = getUrlParameter("track") || default_track;
    if (reset_track)
        track = default_track;

    setQueryStringParameter("filter", urlFilter);
    setQueryStringParameter("program", program);
    setQueryStringParameter("track", track);

    updateToolboxUI(program, urlFilter, track)

    if (program === "all"){
        path_to_papers_json = `papers.json`;
    } else if (track === default_track) {
        path_to_papers_json = `papers_${program}.json`;
    } else {
        path_to_papers_json = `track_${program}_${encodeURIComponent(track)}.json`;
    }

    $('.cards').empty();
    $('#progressBar').show();

    d3.json(path_to_papers_json).then(papers => {
        if(program != "Best"){
            shuffleArray(papers);
        }

        allPapers = papers;

        calcAllKeys(allPapers, allKeys);

        let tracks = [];
        if (program == "main")
            tracks = allTracks;
        else if (program == "workshop")
            tracks = allWorkshops;
        updateTrackList(tracks, track);

        setTypeAhead(urlFilter,
          allKeys, filters, render);

        render();
        
    }).catch(e => console.error(e));
};


/**
 * EVENTS
 * **/

d3.selectAll('.filter_option input').on('click', function () {
    const me = d3.select(this);

    const filter_mode = me.property('value');
    setQueryStringParameter("filter", filter_mode);
    setQueryStringParameter("search", '');
    updateFilterSelectionBtn(filter_mode);


    setTypeAhead(filter_mode, allKeys, filters, render);
    render();
});

d3.selectAll('.remove_session').on('click', () => {
    setQueryStringParameter("session", '');
    render();

});

d3.selectAll('.render_option input').on('click', function () {
    const me = d3.select(this);
    render_mode = me.property('value');

    render();
});

d3.selectAll('.program_option input').on('click', function () {
    const me = d3.select(this);
    let program = me.property('value');
    setQueryStringParameter("program", program);

    start(reset_track=true);
});

d3.select('.visited').on('click', () => {
    sortSelectedFirst(allPapers);

    render();
})

d3.select('.reshuffle').on('click', () => {
    shuffleArray(allPapers);

    render();
})

/**
 * CARDS
 */

const track_html = track => `<option>${track}</option>`;

const keyword = kw => `<a href="papers.html?filter=keywords&search=${kw}"
                       class="text-secondary text-decoration-none">${kw.toLowerCase()}</a>`;

const author_html = author => `<a href="papers.html?program=all&filter=authors&search=${author}">${author}</a>`;

const card_image = (openreview, show) => {
    if (show && openreview.card_image_path && openreview.card_image_path !== '') return ` <center><img class="lazy-load-img cards_img card-img" data-src="${openreview.card_image_path}" onerror="javascript:this.onerror=null;this.src=''" width="80%"/></center>`
    else return ''
};


const card_detail = (openreview, show) => {
    if (show) {
        let str = ''
        if (openreview.content.tldr && openreview.content.tldr != '')
            str += `<br/><p class="card-text"> ${openreview.content.tldr}</p>`
        
        if (openreview.content.keywords 
            && (openreview.content.keywords.length > 1 
                || openreview.content.keywords.length == 1 && openreview.content.keywords[0] !== ""))
            str += `<p class="card-text"><span class="font-weight-bold">Keywords:</span>
                ${openreview.content.keywords.map(keyword).join(', ')}
            </p>`
        
        return str
    } else {
        return ''
    }
};

const card_fav_btn_html = (is_fav) => {
    if (is_fav) {
        return `<button type="button" class="btn btn-sm btn-warning btn-fav" 
                    data-toggle="tooltip" data-placement="left" title="Click to remove from Favorites">
                    <i class="fas fa-star"></i></button>`
    } else {
        return `<button type="button" class="btn btn-sm btn-outline-primary btn-fav"><i class="fas fa-star"></i> Add to Favorites</button>`
    }
}

const program_to_badge_class = new Map()
program_to_badge_class["AISI"] = "primary";
program_to_badge_class["IAAI"] = "danger";
program_to_badge_class["EAAI"] = "danger";
program_to_badge_class["Main"] = "primary";
program_to_badge_class["Demo"] = "warning";
program_to_badge_class["DC"] = "success";
program_to_badge_class["SMT"] = "danger";
program_to_badge_class["SC"] = "warning";
program_to_badge_class["SA"] = "info";
program_to_badge_class["UC"] = "secondary";

const card_program_badge = (paper) => {
    let selected_program = getUrlParameter("program");
    if (selected_program === "all") 
        return `<span class="badge 
                      badge-pill badge-${program_to_badge_class[paper.content.program]}"
                      >${paper.content.program}</span>
                      <span class="badge 
                      badge-pill badge-danger"
                      >${paper.content.best_type_desc}</span>`;
    else if (selected_program === "Main" && "${paper.content.best_type_desc}" !="")
        return `<span class="badge 
              badge-pill badge-danger"
              >${paper.content.best_type_desc}</span>`;
    else if (selected_program === "AISI" && "${paper.content.best_type_desc}" !="")
        return `<span class="badge 
              badge-pill badge-danger"
              >${paper.content.best_type_desc}</span>`;
    else if (selected_program === "Best" && "${paper.content.best_type_desc}" !="")
        return `<span class="badge 
                      badge-pill badge-${program_to_badge_class[paper.content.program]}"
                      >${paper.content.program}</span>
                      <span class="badge 
                      badge-pill badge-danger"
                      >${paper.content.best_type_desc}</span>`;
    else
        return ``;
}

//language=HTML
const card_html = openreview => `
        <div class="card card-paper ${openreview.content.isFav? 'card-fav' : ''}
                card-dimensions${(render_mode == 'detail')? '-detail' : render_mode !== 'list'? '-image' : ''}">
            <div class="card-body">

                <a href="paper_${openreview.id}.html"
                target="_blank"><h5 class="card-title ${openreview.content.read ? 'card-title-visited' : ''}">${openreview.content.title}</h5>
                </a>
                <h6 class="card-subtitle mb-2 text-muted">${openreview.content.authors.join(', ')}</h6>
                
                ${card_program_badge(openreview)}
                ${card_image(openreview, render_mode !== 'list')}
                ${card_detail(openreview, (render_mode === 'detail'))}
            </div>

            <div class="card-footer">
                    ${card_fav_btn_html(openreview.content.isFav)}
                    <button type="button" class="btn btn-sm btn-outline-primary btn-quickview"><i class="fas fa-bars"></i> Quickview</button>
            </div>
        </div>

        `


const modal_keyword = kw => `<a class="badge badge-pill badge-info" 
                                href="papers.html?filter=keywords&search=${kw}">${kw.toLowerCase()}</a>`

const getSessionTimeString = (sess) => {
    let start_time = moment.utc(sess.start_time, 'ddd, DD MMM YYYY HH:mm:ss');
    let end_time = moment.utc(sess.end_time, 'ddd, DD MMM YYYY HH:mm:ss');

    let guess_tz = moment.tz.guess(true);
    let local_start = start_time.tz(guess_tz);
    let local_end = end_time.tz(guess_tz);

    if (local_start.dayOfYear() === local_end.dayOfYear()){
        time_str = `${local_start.format('MMM D, HH:mm')}-${local_end.format('HH:mm')}`;
    } else {
        time_str = `${local_start.format('MMM D HH:mm')}-${local_end.format('MMM D HH:mm')}`;
    }

    return time_str;
}

const getCalendarLinks = (sess, paper) => {
    
    let start_time = moment.utc(sess.start_time, 'ddd, DD MMM YYYY HH:mm:ss');
    let end_time = moment.utc(sess.end_time, 'ddd, DD MMM YYYY HH:mm:ss');

    return addToCalendarData({
        options: {
          class: 'my-class',
          id: 'my-id'
        },
        data: {
          title: paper.content.title.replace("#", " "),
          start: new Date(start_time.format('YYYY-MM-DDTHH:mm:ss')),
          end: new Date(end_time.format('YYYY-MM-DDTHH:mm:ss')),
          timezone: 'UTC',
          address: sess.zoom_link,
          description: `${site_url}/paper_${paper.id}.html`,
        }
    });
}

const modal_session_html = (session, paper) => {
    let calendar_links = getCalendarLinks(session, paper);
    for (const key of Object.keys(calendar_links)) 
        calendar_links[key] = $($.parseHTML(calendar_links[key]))
            .addClass('dropdown-item')
            .prop('outerHTML');
    
    return `<div class="media paper-modal-session">
            <div class="align-self-center mr-2 bg-primary paper-modal-session-name text-light"> 
              ${session.session_name}
            </div>
            <div>
              <div>${getSessionTimeString(session)}</div>
              <div class="btn-group paper-modal-session-calendar-btn">
                <button class="btn btn-link btn-sm dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                  Add to Calendar
                </button>
                <div class="dropdown-menu">  
                    ${calendar_links['google']}
                    ${calendar_links['off365']}
                    ${calendar_links['outlook']}
                    ${calendar_links['ical']}
                </div>
              </div>
            </div>
        </div>`;
}