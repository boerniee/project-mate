class ProductCard extends HTMLElement {
  constructor() {
    super();
    this.addEventListener("click", e => this.consume(e));
  }

  show_modal(title, body) {
    var modal = $('#resultmodal');
    modal.find('.modal-body').text(body);
    modal.find('.modal-header h4').html(title);
    modal.modal('toggle');
  }

  connectedCallback() {
    this.renderDom();
    this.fetchOffer();
  }

  consume(event) {
    if (this.disabled || this.offerid == null) return
    this.fetchOffer();
    $.post({
      url: "/ajax/consume/offer/id".replace('id', this.offerid),
      context: this,
      success: function(data) {
        console.log(data['success']);
        this.show_modal(data['title'], data['text']);
        this.fetchOffer();
      },
      fail: function() {
        alert("fehler");
      }
    });
  }

  set stock(stock) {
    this.shadowRoot.getElementById('stock').innerHTML = " " + stock;
  }

  set price(price) {
    this.shadowRoot.getElementById('price').innerHTML = " " + price;
  }

  get disabled() {
    return this.hasAttribute('disabled');
  }

  set disabled(val) {
    if (val) {
      this.setAttribute('disabled', '');
    } else {
      this.removeAttribute('disabled');
    }
  }

  get productId() {
    return this.getAttribute('productid')
  }

  set badge(text) {
    var badge = document.createElement('div');
    badge.setAttribute('id', 'badge');
    badge.setAttribute('class', 'card-badge');
    badge.setAttribute('style', 'position:absolute;top:-10px;left:-30px;padding:5px;background:blue;color:white;transform:rotate(-20deg);');
    badge.innerHTML = text;
    this.shadowRoot.appendChild(badge);
  }

  set productId(id) {
    if (id==null) {
      this.removeAttribute('productid');
    } else {
      this.setAttribute('productid', id);
    }
  }

  fetchOffer() {
    $.get({
      url: "/ajax/product/id/offer".replace('id', this.getAttribute('productid')),
      context: this,
      success: function(data) {
        if (data['found']) {
          this.stock = data['offer']['stock'];
          this.price = data['offer']['price'];
          this.offerid = data['offer']['id'];
          this.disabled = false;
        } else {
          this.stock = "-"
          this.price = "-"
          this.badge = data['text'];
        }
      },
      fail: function() {
        alert("fehler");
      }
    });
  }

  renderDom() {
    this.setAttribute('class', 'card mb-3');
    this.setAttribute('disabled', "");
    var shadow = this.attachShadow({mode: 'open'});
    var rowDiv = document.createElement('div');
    rowDiv.setAttribute('class','row no-gutters');

    var imageContainer = document.createElement('div');
    imageContainer.setAttribute('class', 'col-md-4');
    rowDiv.appendChild(imageContainer);

    var image = document.createElement('img');
    image.setAttribute('class','card-img');
    image.setAttribute('alt', '...');
    image.setAttribute('src', this.getAttribute('image'));
    imageContainer.appendChild(image);

    var body = document.createElement('div');
    body.setAttribute('class', 'col-md-8');
    rowDiv.appendChild(body);

    var cardBody = document.createElement('div');
    cardBody.setAttribute('class', 'card-body');
    cardBody.setAttribute('style', 'padding: 1rem;');
    body.appendChild(cardBody);

    var cardTitle = document.createElement('h5');
    cardTitle.setAttribute('class', 'card-title');
    cardTitle.setAttribute('id', 'title');
    //cardTitle.innerHTML = this.getAttribute('description');
    cardBody.appendChild(cardTitle);

    var cardText = document.createElement('p');
    cardText.setAttribute('class', 'card-text');

    var cardPrice = document.createElement('i');
    cardPrice.setAttribute('class', 'fas fa-money-bill-wave');
    cardText.appendChild(cardPrice);

    var price = document.createElement('span');
    price.setAttribute('id', 'price');
    price.innerHTML = " <span class='fas fa-sync fa-spin' role='status' aria-hidden='true'></span>";
    cardText.appendChild(price);

    var br = document.createElement('br');
    cardText.appendChild(br);

    var cardStock = document.createElement('i');
    cardStock.setAttribute('class', 'fas fa-boxes');
    cardText.appendChild(cardStock);

    var stock = document.createElement('span');
    stock.setAttribute('id', 'stock');
    stock.innerHTML = " <span class='fas fa-sync fa-spin' role='status' aria-hidden='true'></span>";
    cardText.appendChild(stock);
    shadow.innerHTML = '<style>.card .card-badge {position:absolute;top:-10px;left:-30px;padding:5px;background:blue;color:white;transform:rotate(-20deg);}</style><link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css" integrity="sha384-GJzZqFGwb1QTTN6wy59ffF1BuGJpLSa9DkKMp0DgiMDm4iYMj70gZWKYbI706tWS" crossorigin="anonymous"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.11.2/css/all.css">'
    cardBody.appendChild(cardText);
    shadow.appendChild(rowDiv);
    return
  }
}

customElements.define('product-card', ProductCard, { extends: 'div' });
